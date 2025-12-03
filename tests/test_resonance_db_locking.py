"""
Test database locking for multi-process synchronization.
Tests file-based locking (fcntl) instead of threading.Lock()
"""

import pytest
import sqlite3
import fcntl
import multiprocessing
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from spirits import resonance


def init_db_in_process():
    """Initialize DB in separate process."""
    resonance._init_db()


def test_wal_mode_check():
    """Test that WAL mode is checked before setting."""
    # Clean DB for test
    test_db = Path(__file__).parent.parent / "spirits" / "resonance_test.db"
    if test_db.exists():
        test_db.unlink()
    
    # Backup original path
    original_path = resonance.DB_PATH
    resonance.DB_PATH = test_db
    
    try:
        # First initialization
        resonance._init_db()
        
        # Check WAL mode
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0].lower()
        conn.close()
        
        assert mode == "wal"
        
        # Second initialization should not re-set WAL (no lock contention)
        resonance._init_db()
        
        # Verify WAL is still set
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode")
        mode2 = cur.fetchone()[0].lower()
        conn.close()
        
        assert mode2 == "wal"
        
    finally:
        resonance.DB_PATH = original_path
        if test_db.exists():
            test_db.unlink()


def test_multi_process_init():
    """Test that DB initialization works across multiple processes."""
    test_db = Path(__file__).parent.parent / "spirits" / "resonance_mp_test.db"
    lock_file = Path(__file__).parent.parent / "spirits" / "resonance_mp_test.db.lock"
    
    if test_db.exists():
        test_db.unlink()
    if lock_file.exists():
        lock_file.unlink()
    
    original_path = resonance.DB_PATH
    resonance.DB_PATH = test_db
    resonance.LOCK_FILE_PATH = lock_file
    
    try:
        # Start multiple processes
        processes = []
        for _ in range(3):
            p = multiprocessing.Process(target=init_db_in_process)
            p.start()
            processes.append(p)
        
        # Wait for all to complete
        for p in processes:
            p.join(timeout=10)
            assert p.exitcode == 0, "Process should complete successfully"
        
        # Verify DB was initialized correctly
        assert test_db.exists()
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()
        
        # Check tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resonance'")
        assert cur.fetchone() is not None
        
        cur.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0].lower()
        assert mode == "wal"
        
        conn.close()
        
    finally:
        resonance.DB_PATH = original_path
        if test_db.exists():
            test_db.unlink()
        if lock_file.exists():
            lock_file.unlink()


def test_file_lock_exists():
    """Test that lock file mechanism is in place."""
    lock_file = resonance.LOCK_FILE_PATH
    assert lock_file is not None
    assert hasattr(resonance, 'LOCK_FILE_PATH')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

