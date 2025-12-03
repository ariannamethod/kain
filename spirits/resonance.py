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
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any


DB_PATH = Path(__file__).parent / "resonance.db"

# Thread-safe initialization flag
_db_initialized = False
_init_lock = threading.Lock()


def _init_db() -> None:
    """
    Initialize resonance database with full schema (thread-safe, called once).

    This function is called automatically on first use.
    WAL mode is enabled for concurrent reads/writes.
    """
    global _db_initialized

    # Quick check without lock (optimization)
    if _db_initialized:
        return

    # Thread-safe initialization
    with _init_lock:
        # Double-check after acquiring lock
        if _db_initialized:
            return

        conn = sqlite3.connect(DB_PATH, timeout=10.0)  # 10 second timeout
        cur = conn.cursor()

        # Enable WAL mode for concurrent reads/writes
        # This allows multiple readers + one writer simultaneously
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

        # Mark as initialized
        _db_initialized = True


def log(role: str, content: str) -> None:
    """
    Legacy logging function (backwards compatible with memory.py).

    Args:
        role: 'user' | 'kain_user' | 'kain' | 'abel' | etc
        content: Message content
    """
    conn = sqlite3.connect(DB_PATH, timeout=10.0)  # 10 second timeout
    cur = conn.cursor()

    # Write to legacy events table
    cur.execute("INSERT INTO events VALUES (?, ?, ?)", (time.time(), role, content))

    # Also write to resonance table with proper structure
    daemon = _role_to_daemon(role)
    event_type = "observation" if "_user" in role else "reflection"

    log_resonance(
        daemon=daemon,
        event_type=event_type,
        content=content
    )

    conn.commit()
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
    conn.close()

    return row_id


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
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

    return row_id


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
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

    return row_id


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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn.close()

    return [dict(row) for row in rows]


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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn.close()

    return [dict(row) for row in rows]


def increment_memory_access(memory_id: int) -> None:
    """Increment access count and update last_access timestamp for a memory."""
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()


def get_kernel_adaptations(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve recent kernel adaptations.

    Args:
        limit: Max number of adaptations

    Returns:
        List of adaptation dicts
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM kernel_adaptations ORDER BY ts DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


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
    conn = sqlite3.connect(DB_PATH)
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

    conn.close()

    if len(charges) < 2:
        return 0.0

    # Compute variance in affective charge (instability)
    mean_charge = sum(charges) / len(charges)
    variance = sum((c - mean_charge) ** 2 for c in charges) / len(charges)

    # Dissonance = variance + adaptation_rate
    dissonance = variance + (adaptation_count / 10.0)

    return min(dissonance, 1.0)


# Legacy functions for backwards compatibility
def last_user_command() -> str:
    """Get last user command (legacy)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content FROM events WHERE role='user' ORDER BY ts DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


def last_real_command() -> str:
    """Get last real command (not daemon query)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content FROM events
        WHERE role='user' AND content NOT LIKE '/%'
        ORDER BY ts DESC LIMIT 1
        """
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


# Initialize database on module load
_init_db()
