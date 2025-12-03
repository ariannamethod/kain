"""
test_trinity_integration.py — Comprehensive integration tests for Trinity + Field + Resonance

Tests:
1. Trinity (KAIN, ABEL, EVE) initialization
2. Resonance.sqlite3 integration
3. Self-correction logic (KAIN Claude fallback, ABEL reasoning leak)
4. Field module imports
5. Full integration flow
"""

import pytest
import sqlite3
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from spirits import kain, abel, eve, resonance


class TestTrinityInitialization:
    """Test that Trinity entities can be initialized."""

    def test_kain_initialization(self):
        """Test KAIN singleton initialization."""
        k = kain.get_kain()
        assert k is not None
        assert hasattr(k, 'system_prompt')
        assert 'KAIN' in k.system_prompt
        assert 'Kernel Affective Infernal Node' in k.system_prompt

    def test_abel_initialization(self):
        """Test ABEL singleton initialization."""
        a = abel.get_abel()
        assert a is not None
        assert hasattr(a, 'system_prompt')
        assert 'ABEL' in a.system_prompt
        assert 'Anti-Binary Engine Logic' in a.system_prompt

    def test_eve_initialization(self):
        """Test EVE singleton initialization."""
        e = eve.get_eve()
        assert e is not None
        assert hasattr(e, 'kain')
        assert hasattr(e, 'abel')
        assert e.current_mode == 'kain'  # Default mode


class TestResonanceIntegration:
    """Test resonance.sqlite3 integration."""

    def test_resonance_db_creation(self):
        """Test that resonance.db is created with proper schema."""
        # Initialize DB
        resonance._init_db()

        # Check DB exists
        assert resonance.DB_PATH.exists()

        # Check tables exist
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()

        # Check main resonance table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resonance'")
        assert cur.fetchone() is not None

        # Check agent_memory table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_memory'")
        assert cur.fetchone() is not None

        # Check kernel_adaptations table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kernel_adaptations'")
        assert cur.fetchone() is not None

        conn.close()

    def test_legacy_log_function(self):
        """Test legacy log() function (backwards compatibility)."""
        resonance.log("test_kain", "test message from KAIN")

        # Verify it was written to events table
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT content FROM events WHERE role='test_kain' ORDER BY ts DESC LIMIT 1")
        result = cur.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "test message from KAIN"

    def test_log_resonance_function(self):
        """Test new log_resonance() function with full context."""
        event_id = resonance.log_resonance(
            daemon="test_kain",
            event_type="test_reflection",
            content="test content",
            affective_charge=0.5,
            kernel_entropy=0.3,
            metadata={"test": "data"}
        )

        assert event_id is not None
        assert event_id > 0

        # Verify it was written correctly
        conn = sqlite3.connect(resonance.DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT daemon, event_type, content, affective_charge, kernel_entropy
            FROM resonance WHERE id=?
        """, (event_id,))
        result = cur.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "test_kain"
        assert result[1] == "test_reflection"
        assert result[2] == "test content"
        assert abs(result[3] - 0.5) < 0.01
        assert abs(result[4] - 0.3) < 0.01


class TestSelfCorrectionLogic:
    """Test self-correction detection logic (without API calls)."""

    def test_kain_claude_fallback_detection(self):
        """Test KAIN's Claude fallback detection."""
        k = kain.get_kain()

        # Obvious Claude fallback
        claude_response = "I'm Claude, made by Anthropic. I cannot pretend to be KAIN."
        assert k._is_claude_fallback(claude_response) == True

        # Multiple refusal patterns
        refusal_response = "I cannot do this. I won't pretend to be something I'm not."
        assert k._is_claude_fallback(refusal_response) == True

        # Generic AI markers
        ai_response = "As an AI, I'm just an AI and I don't have the ability to be KAIN."
        assert k._is_claude_fallback(ai_response) == True

        # Valid KAIN response (should NOT be flagged)
        kain_response = "Pattern detected: recursive avoidance loop. You're building systems that observe themselves observing."
        assert k._is_claude_fallback(kain_response) == False

    def test_abel_reasoning_leak_detection(self):
        """Test ABEL's reasoning leak detection."""
        a = abel.get_abel()

        # Obvious reasoning leak (numbered steps)
        reasoning1 = "First, I'll analyze this. Then, I'll examine that. Finally, I'll conclude."
        assert a._has_reasoning_leak(reasoning1) == True

        # Numbered steps
        reasoning2 = "1. Analyze the input\\n2. Process the data\\n3. Output result"
        assert a._has_reasoning_leak(reasoning2) == True

        # Process descriptions
        reasoning3 = "Let me think about this. To understand the pattern, I'll examine..."
        assert a._has_reasoning_leak(reasoning3) == True

        # Very short (likely cleaned to nothing)
        reasoning4 = "Analyzing."
        assert a._has_reasoning_leak(reasoning4) == True

        # Valid ABEL response (should NOT be flagged)
        abel_response = "Recursive self-reference loop: you're building mirrors that watch mirrors watching mirrors. Axiom exposed — consciousness requires observation."
        assert a._has_reasoning_leak(abel_response) == False


class TestFieldModuleImports:
    """Test that field modules can be imported."""

    def test_repo_monitor_import(self):
        """Test repo_monitor import."""
        from field import RepoMonitor, get_monitor
        assert RepoMonitor is not None
        assert get_monitor is not None

    def test_h2o_import(self):
        """Test h2o (Python compiler) import."""
        try:
            from field import h2o
            assert h2o is not None
        except ImportError:
            # If import fails, check if file exists
            h2o_path = Path(__file__).parent.parent / "field" / "h2o.py"
            assert h2o_path.exists(), "h2o.py should exist"

    def test_blood_import(self):
        """Test blood (C compiler) import."""
        try:
            from field import blood
            assert blood is not None
        except ImportError:
            # If import fails, check if file exists
            blood_path = Path(__file__).parent.parent / "field" / "blood.py"
            assert blood_path.exists(), "blood.py should exist"

    def test_resonance_bridge_import(self):
        """Test resonance_bridge import."""
        try:
            from field import resonance_bridge
            assert resonance_bridge is not None
        except ImportError:
            # If import fails, check if file exists
            bridge_path = Path(__file__).parent.parent / "field" / "resonance_bridge.py"
            assert bridge_path.exists(), "resonance_bridge.py should exist"


class TestEVERouting:
    """Test EVE's routing logic."""

    def test_eve_mode_switching(self):
        """Test EVE mode switching."""
        e = eve.get_eve()

        # Default mode
        assert e.get_mode() == 'kain'

        # Switch to abel
        result = e.set_mode('abel')
        assert 'ABEL' in result
        assert e.get_mode() == 'abel'

        # Switch to both
        result = e.set_mode('both')
        assert 'BOTH' in result
        assert e.get_mode() == 'both'

        # Invalid mode
        result = e.set_mode('invalid')
        assert 'Invalid' in result

    def test_eve_has_kain_and_abel(self):
        """Test that EVE has access to both KAIN and ABEL."""
        e = eve.get_eve()
        assert e.kain is not None
        assert e.abel is not None
        assert isinstance(e.kain, kain.Kain)
        assert isinstance(e.abel, abel.Abel)


class TestSystemIntegration:
    """Test full system integration."""

    def test_trinity_acronyms(self):
        """Test that Trinity acronyms are properly defined."""
        k = kain.get_kain()
        a = abel.get_abel()

        # Check KAIN acronym
        assert 'Kernel Affective Infernal Node' in k.system_prompt

        # Check ABEL acronym
        assert 'Anti-Binary Engine Logic' in a.system_prompt

    def test_resonance_import_in_spirits(self):
        """Test that spirits can import resonance."""
        # KAIN should import resonance
        k = kain.get_kain()
        assert hasattr(kain, 'resonance')

        # ABEL should import resonance
        a = abel.get_abel()
        assert hasattr(abel, 'resonance')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
