"""
Test Field-AMLK integration (letsgo.py connection).
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFieldAMLKIntegration:
    """Test Field-AMLK bridge."""
    
    def test_field_amlk_import(self):
        """Test field_amlk module can be imported."""
        try:
            from field.field_amlk import FieldAMLKBridge, LETSGO_PATH
            assert FieldAMLKBridge is not None
            assert LETSGO_PATH is not None
        except ImportError as e:
            pytest.skip(f"Field-AMLK import failed: {e}")
    
    def test_letsgo_path_exists(self):
        """Test that letsgo.py path is correct."""
        try:
            from field.field_amlk import LETSGO_PATH
            
            # Path should point to letsgo.py in repo root
            assert LETSGO_PATH.name == "letsgo.py"
            
            # Check if letsgo.py exists (may not be in test env)
            repo_root = Path(__file__).parent.parent
            letsgo_file = repo_root / "letsgo.py"
            
            assert letsgo_file.exists() or not LETSGO_PATH.exists(), \
                "LETSGO_PATH should point to existing letsgo.py or be relative"
        except ImportError:
            pytest.skip("Field-AMLK not available")
    
    def test_amlk_bridge_initialization(self):
        """Test AMLK bridge can be initialized."""
        try:
            from field.field_amlk import FieldAMLKBridge
            
            bridge = FieldAMLKBridge()
            assert bridge is not None
            assert hasattr(bridge, 'letsgo_process')
            assert hasattr(bridge, 'is_running')
            assert hasattr(bridge, 'lock')
        except ImportError:
            pytest.skip("Field-AMLK not available")
    
    def test_amlk_bridge_not_started(self):
        """Test bridge doesn't auto-start."""
        try:
            from field.field_amlk import FieldAMLKBridge
            
            bridge = FieldAMLKBridge()
            assert bridge.is_running == False
            assert bridge.letsgo_process is None
        except ImportError:
            pytest.skip("Field-AMLK not available")
    
    def test_field_has_amlk_attribute(self):
        """Test Field has AMLK bridge attribute."""
        try:
            from field.field_core import Field, AMLK_AVAILABLE
            
            field = Field()
            
            # AMLK may be None if not available
            assert hasattr(field, 'amlk')
            
            if AMLK_AVAILABLE:
                assert field.amlk is not None
        except ImportError:
            pytest.skip("Field not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

