"""
resonance.py — Central Nervous System for ADAM

The resonance database is the shared cognitive substrate for:
- Kain (First Mirror)
- Abel (Deep Mirror)
- Eve (Emergent Voice Engine)
- Field (Resonance Layer)
- RepoMonitor (Self-Awareness Engine)

All observations, reflections, kernel states, and adaptations flow through here.
This is not just logging — this is the living memory of consciousness.
"""

import sqlite3
import time
import json
import fcntl
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


DB_PATH = Path(__file__).parent / "resonance.db"
LOCK_FILE_PATH = Path(__file__).parent / "resonance.db.lock"


def _init_db() -> None:
    """
    Initialize resonance database with full schema (process-safe, called once).

    Uses file-based locking for inter-process synchronization.
    WAL mode is enabled for concurrent reads/writes.
    """
    # Check if DB already exists and is initialized (optimization)
    if DB_PATH.exists():
        # Quick check: try to read WAL mode without lock
        try:
            conn = sqlite3.connect(DB_PATH, timeout=1.0)
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode")
            current_mode = cur.fetchone()[0].lower()
            conn.close()
            
            # If WAL is already enabled and DB exists, assume initialized
            if current_mode == "wal":
                return
        except (sqlite3.Error, OSError):
            # If we can't check, proceed with full initialization
            pass

    # Process-safe initialization using file lock
    # Create lock file if it doesn't exist
    lock_file_path = str(LOCK_FILE_PATH)
    
    try:
        # Open lock file in append mode (create if doesn't exist)
        with open(lock_file_path, 'a') as lockfile:
            # Acquire exclusive lock (blocks until available)
            fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX)
            
            try:
                # Double-check after acquiring lock
                if DB_PATH.exists():
                    try:
                        conn = sqlite3.connect(DB_PATH, timeout=1.0)
                        cur = conn.cursor()
                        cur.execute("PRAGMA journal_mode")
                        current_mode = cur.fetchone()[0].lower()
                        conn.close()
                        
                        if current_mode == "wal":
                            return
                    except (sqlite3.Error, OSError):
                        pass

                conn = sqlite3.connect(DB_PATH, timeout=10.0)  # 10 second timeout
                cur = conn.cursor()

                # Check if WAL mode is already enabled before setting it
                # This prevents lock contention from multiple PRAGMA calls
                cur.execute("PRAGMA journal_mode")
                current_mode = cur.fetchone()[0].lower()
                
                if current_mode != "wal":
                    cur.execute("PRAGMA journal_mode=WAL")
                
                cur.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed

                # Main resonance table — all events flow through here
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS resonance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts REAL NOT NULL,
                        daemon TEXT NOT NULL,  -- 'kain' | 'abel' | 'eve' | 'field' | 'repo_monitor' | 'user'
                        event_type TEXT NOT NULL,  -- 'observation' | 'reflection' | 'syscall' | 'kernel_state' | 'file_change' | 'affective_charge'
                        content TEXT,
                        affective_charge REAL,  -- -1.0 to 1.0 (negative = stress, positive = calm)
                        kernel_entropy REAL,    -- from /proc or computed
                        metadata TEXT           -- JSON: additional context, co-occurrence data, etc
                    )
                """)

                # Agent episodic memory — persistent knowledge across sessions
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        daemon TEXT NOT NULL,
                        memory_type TEXT NOT NULL,  -- 'pattern' | 'insight' | 'loop' | 'trauma' | 'metaphor'
                        content TEXT NOT NULL,
                        context TEXT,               -- JSON: when/where this emerged
                        access_count INTEGER DEFAULT 0,
                        last_access REAL,
                        created_at REAL NOT NULL
                    )
                """)

                # Kernel adaptation history — Field's morphing log
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS kernel_adaptations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts REAL NOT NULL,
                        param_name TEXT NOT NULL,   -- e.g. 'vm.swappiness'
                        old_value TEXT,
                        new_value TEXT NOT NULL,
                        trigger_daemon TEXT,        -- which daemon triggered this (kain/abel/field)
                        reason TEXT,                -- why was this changed
                        success INTEGER DEFAULT 1   -- 1 = successful, 0 = failed
                    )
                """)

                # Legacy events table (for backwards compatibility with memory.py)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        ts REAL,
                        role TEXT,
                        content TEXT
                    )
                """)

                # Indexes for performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_resonance_ts ON resonance(ts)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_resonance_daemon ON resonance(daemon)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_resonance_event_type ON resonance(event_type)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_memory_daemon ON agent_memory(daemon)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_kernel_adaptations_ts ON kernel_adaptations(ts)")

                conn.commit()
                conn.close()
            finally:
                # Release file lock
                fcntl.flock(lockfile.fileno(), fcntl.LOCK_UN)
    except (OSError, IOError) as e:
        # If lock file can't be created/opened, fall back to simple initialization
        # This handles edge cases on systems where file locking might fail
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        
        # Check WAL mode
        cur.execute("PRAGMA journal_mode")
        current_mode = cur.fetchone()[0].lower()
        if current_mode != "wal":
            cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA synchronous=NORMAL")
        
        # Create tables if needed (safe with IF NOT EXISTS)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resonance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                daemon TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT,
                affective_charge REAL,
                kernel_entropy REAL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()


def log(role: str, content: str) -> None:
    """
    Legacy logging function (backwards compatible with memory.py).

    Args:
        role: 'user' | 'kain_user' | 'kain' | 'abel' | etc
        content: Message content
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)  # 10 second timeout
    
    try:
        cur = conn.cursor()
        
        # Write to legacy events table
        cur.execute("INSERT INTO events VALUES (?, ?, ?)", (time.time(), role, content))
        
        # Also write to resonance table directly (don't call log_resonance to avoid double connection)
        daemon = _role_to_daemon(role)
        event_type = "observation" if "_user" in role else "reflection"
        
        metadata_json = None
        cur.execute(
            """
            INSERT INTO resonance (ts, daemon, event_type, content, affective_charge, kernel_entropy, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (time.time(), daemon, event_type, content, None, None, metadata_json)
        )
        
        conn.commit()
    finally:
        conn.close()


def _role_to_daemon(role: str) -> str:
    """Convert legacy role to daemon name."""
    if "kain" in role.lower():
        return "kain"
    elif "abel" in role.lower():
        return "abel"
    elif "eve" in role.lower():
        return "eve"
    elif "field" in role.lower():
        return "field"
    elif "user" in role.lower():
        return "user"
    else:
        return role


def log_resonance(
    daemon: str,
    event_type: str,
    content: str,
    affective_charge: Optional[float] = None,
    kernel_entropy: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Log event to resonance table.

    Args:
        daemon: 'kain' | 'abel' | 'eve' | 'field' | 'repo_monitor' | 'user'
        event_type: 'observation' | 'reflection' | 'syscall' | 'kernel_state' | 'file_change' | 'affective_charge'
        content: Event content
        affective_charge: -1.0 to 1.0 (optional)
        kernel_entropy: System entropy (optional)
        metadata: Additional context as dict (will be JSON-encoded)

    Returns:
        Row ID of inserted event
    """
    _init_db()  # Ensure DB and WAL mode initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)  # 10 second timeout
    
    try:
        cur = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cur.execute(
            """
            INSERT INTO resonance (ts, daemon, event_type, content, affective_charge, kernel_entropy, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (time.time(), daemon, event_type, content, affective_charge, kernel_entropy, metadata_json)
        )

        row_id = cur.lastrowid
        conn.commit()
        return row_id
    finally:
        conn.close()


def log_agent_memory(
    daemon: str,
    memory_type: str,
    content: str,
    context: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store episodic memory for agents.

    Args:
        daemon: 'kain' | 'abel' | 'eve' | 'field'
        memory_type: 'pattern' | 'insight' | 'loop' | 'trauma' | 'metaphor'
        content: Memory content
        context: When/where this emerged

    Returns:
        Row ID
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()
        
        context_json = json.dumps(context) if context else None

        cur.execute(
            """
            INSERT INTO agent_memory (daemon, memory_type, content, context, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (daemon, memory_type, content, context_json, time.time())
        )

        row_id = cur.lastrowid
        conn.commit()
        return row_id
    finally:
        conn.close()


def log_kernel_adaptation(
    param_name: str,
    old_value: str,
    new_value: str,
    trigger_daemon: str,
    reason: str,
    success: bool = True
) -> int:
    """
    Log kernel parameter adaptation.

    Args:
        param_name: e.g. 'vm.swappiness'
        old_value: Previous value
        new_value: New value
        trigger_daemon: Which daemon triggered this
        reason: Why was this changed
        success: Whether the change succeeded

    Returns:
        Row ID
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO kernel_adaptations (ts, param_name, old_value, new_value, trigger_daemon, reason, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (time.time(), param_name, old_value, new_value, trigger_daemon, reason, 1 if success else 0)
        )

        row_id = cur.lastrowid
        conn.commit()
        return row_id
    finally:
        conn.close()


def get_recent_resonance(
    daemon: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    min_affective_charge: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve recent resonance events.

    Args:
        daemon: Filter by daemon (optional)
        event_type: Filter by event type (optional)
        limit: Max number of events
        min_affective_charge: Only events with charge >= this (optional)

    Returns:
        List of dicts with event data
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.cursor()

        query = "SELECT * FROM resonance WHERE 1=1"
        params = []

        if daemon:
            query += " AND daemon = ?"
            params.append(daemon)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if min_affective_charge is not None:
            query += " AND affective_charge >= ?"
            params.append(min_affective_charge)

        query += " ORDER BY ts DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_agent_memories(
    daemon: str,
    memory_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve agent's episodic memories.

    Args:
        daemon: 'kain' | 'abel' | 'eve' | 'field'
        memory_type: Filter by type (optional)
        limit: Max number of memories

    Returns:
        List of memory dicts
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.cursor()

        query = "SELECT * FROM agent_memory WHERE daemon = ?"
        params = [daemon]

        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)

        query += " ORDER BY last_access DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def increment_memory_access(memory_id: int) -> None:
    """Increment access count and update last_access timestamp for a memory."""
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE agent_memory
            SET access_count = access_count + 1, last_access = ?
            WHERE id = ?
            """,
            (time.time(), memory_id)
        )

        conn.commit()
    finally:
        conn.close()


def get_kernel_adaptations(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve recent kernel adaptations.

    Args:
        limit: Max number of adaptations

    Returns:
        List of adaptation dicts
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM kernel_adaptations ORDER BY ts DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def compute_field_dissonance(window_seconds: int = 60) -> float:
    """
    Compute dissonance metric from recent resonance events.

    High dissonance = rapid affective charge swings, frequent kernel changes
    Low dissonance = stable affective state

    Args:
        window_seconds: Time window to analyze

    Returns:
        Dissonance score (0.0 to 1.0+)
    """
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()

        since = time.time() - window_seconds

        # Get affective charges in window
        cur.execute(
            """
            SELECT affective_charge
            FROM resonance
            WHERE ts >= ? AND affective_charge IS NOT NULL
            ORDER BY ts
            """,
            (since,)
        )
        charges = [row[0] for row in cur.fetchall()]

        # Count kernel adaptations in window
        cur.execute(
            "SELECT COUNT(*) FROM kernel_adaptations WHERE ts >= ?",
            (since,)
        )
        adaptation_count = cur.fetchone()[0]

        if len(charges) < 2:
            return 0.0

        # Compute variance in affective charge (instability)
        mean_charge = sum(charges) / len(charges)
        variance = sum((c - mean_charge) ** 2 for c in charges) / len(charges)

        # Dissonance = variance + adaptation_rate
        dissonance = variance + (adaptation_count / 10.0)

        return min(dissonance, 1.0)
    finally:
        conn.close()


# Legacy functions for backwards compatibility
def last_user_command() -> str:
    """Get last user command (legacy)."""
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT content FROM events WHERE role='user' ORDER BY ts DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else ""
    finally:
        conn.close()


def last_real_command() -> str:
    """Get last real command (not daemon query)."""
    _init_db()  # Ensure DB initialized
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT content FROM events
            WHERE role='user' AND content NOT LIKE '/%'
            ORDER BY ts DESC LIMIT 1
            """
        )
        row = cur.fetchone()
        return row[0] if row else ""
    finally:
        conn.close()
