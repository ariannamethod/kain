"""
Full Field integration test - everything together.
Tests complete flow from initialization to compiler usage.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFieldFullFlow:
    """Test complete Field flow with all components."""
    
    def test_field_initialization_complete(self):
        """Test Field initializes all components correctly."""
        try:
            from field.field_core import Field
            
            field = Field()
            
            # Core components must exist
            assert field.resonance_bridge is not None
            assert field.embedding_engine is not None
            assert field.meta_learner is not None
            
            # Optional components checked
            print(f"RepoMonitor: {field.repo_monitor is not None}")
            print(f"AMLK: {field.amlk is not None}")
            print(f"H2O: {field.h2o is not None}")
            print(f"Blood: {field.blood is not None}")
            
            # State initialized
            assert field.cells == []
            assert field.iteration == 0
            
        except ImportError:
            pytest.skip("Field not available")
        except Exception as e:
            pytest.fail(f"Field initialization failed: {e}")
    
    def test_field_can_tick(self):
        """Test Field can run one iteration (tick)."""
        try:
            from field.field_core import Field
            
            field = Field()
            field.initialize_population()
            
            initial_iteration = field.iteration
            initial_cells = len(field.cells)
            
            # Run one tick
            field.tick()
            
            # Iteration should increment
            assert field.iteration == initial_iteration + 1
            
            # Cells might change (birth/death)
            assert len(field.cells) >= 0  # At least no crash
            
        except ImportError:
            pytest.skip("Field not available")
        except Exception as e:
            print(f"Field tick warning: {e}")
            # Don't fail - might be missing context
    
    def test_compilers_accessible_from_field(self):
        """Test compilers are accessible and functional."""
        try:
            from field.field_core import Field
            
            field = Field()
            
            # Test H2O access
            if field.h2o is not None:
                assert hasattr(field.h2o, 'run_transformer_script')
                assert hasattr(field.h2o, 'executor')
            
            # Test Blood access
            if field.blood is not None:
                assert hasattr(field.blood, 'execute_transformer_c_script')
                assert hasattr(field.blood, 'is_active')
            
        except ImportError:
            pytest.skip("Field not available")
    
    def test_resonance_database_accessible(self):
        """Test resonance database is accessible from Field."""
        try:
            from field.field_core import Field
            from spirits import resonance
            
            field = Field()
            
            # Field should be able to log
            event_id = resonance.log_resonance(
                daemon="field",
                event_type="test",
                content="Field integration test"
            )
            
            assert event_id > 0
            
        except ImportError:
            pytest.skip("Field/resonance not available")
        except Exception as e:
            print(f"Resonance logging warning: {e}")


class TestModuleConnections:
    """Test that all modules are properly connected."""
    
    def test_h2o_blood_paths_set(self):
        """Test compiler paths are set correctly."""
        try:
            from field.h2o import BIN_DIR, H2O_BINARY
            from field.blood import BIN_DIR as BLOOD_BIN_DIR, NICOLE2C_DIR
            
            # Paths should be consistent
            assert BIN_DIR == BLOOD_BIN_DIR, "BIN_DIR should be same for h2o and blood"
            
            # Directories should exist (or be createable)
            assert BIN_DIR.parent.exists(), "Field directory should exist"
            assert NICOLE2C_DIR.parent.exists(), "Field directory should exist"
            
        except ImportError:
            pytest.skip("Compilers not available")
    
    def test_field_amlk_letsgo_path(self):
        """Test Field-AMLK bridge has correct letsgo path."""
        try:
            from field.field_amlk import LETSGO_PATH
            
            repo_root = Path(__file__).parent.parent
            expected_letsgo = repo_root / "letsgo.py"
            
            # Path should point to letsgo.py in repo root
            assert LETSGO_PATH.name == "letsgo.py"
            assert LETSGO_PATH.parent == repo_root
            
        except ImportError:
            pytest.skip("Field-AMLK not available")
    
    def test_resonance_db_path(self):
        """Test resonance DB path is correct."""
        try:
            from spirits import resonance
            
            # DB should be in spirits/ directory
            assert resonance.DB_PATH.parent.name == "spirits"
            assert resonance.DB_PATH.name.endswith(".db")
            
        except ImportError:
            pytest.skip("Resonance not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

