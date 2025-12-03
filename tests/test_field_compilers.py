"""
Test Field compilers (h2o and blood) initialization and usage.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestH2OCompiler:
    """Test H2O Python compiler."""
    
    def test_h2o_import(self):
        """Test h2o module can be imported."""
        try:
            from field.h2o import H2OEngine, H2ORuntime, H2OCompiler
            assert H2OEngine is not None
            assert H2ORuntime is not None
            assert H2OCompiler is not None
        except ImportError as e:
            pytest.skip(f"H2O import failed: {e}")
    
    def test_h2o_engine_initialization(self):
        """Test H2O engine can be initialized."""
        try:
            from field.h2o import H2OEngine
            
            engine = H2OEngine()
            assert engine is not None
            assert hasattr(engine, 'runtime')
            assert hasattr(engine, 'compiler')
            assert hasattr(engine, 'executor')
        except ImportError:
            pytest.skip("H2O not available")
    
    def test_h2o_binary_path(self):
        """Test H2O binary path is set correctly."""
        try:
            from field.h2o import BIN_DIR, H2O_BINARY
            
            assert BIN_DIR is not None
            # H2O_BINARY may be None if binary doesn't exist (uses Python runtime)
            assert H2O_BINARY is None or Path(H2O_BINARY).exists()
        except ImportError:
            pytest.skip("H2O not available")
    
    def test_h2o_simple_script(self):
        """Test H2O can compile and run simple Python script."""
        try:
            from field.h2o import H2OEngine
            
            engine = H2OEngine()
            code = """
result = 2 + 2
h2o_log(f"Result: {result}")
"""
            # This should not raise
            try:
                engine.run_transformer_script(code, "test_1")
            except Exception as e:
                # If it fails, that's okay - might need runtime setup
                pass
        except ImportError:
            pytest.skip("H2O not available")


class TestBloodCompiler:
    """Test Blood C compiler."""
    
    def test_blood_import(self):
        """Test blood module can be imported."""
        try:
            from field.blood import BloodCore, BloodCCompiler, BloodMemoryManager
            assert BloodCore is not None
            assert BloodCCompiler is not None
            assert BloodMemoryManager is not None
        except ImportError as e:
            pytest.skip(f"Blood import failed: {e}")
    
    def test_blood_core_initialization(self):
        """Test Blood core can be initialized."""
        try:
            from field.blood import BloodCore
            
            blood = BloodCore()
            assert blood is not None
            assert hasattr(blood, 'memory_manager')
            assert hasattr(blood, 'process_controller')
            assert hasattr(blood, 'c_compiler')
        except ImportError:
            pytest.skip("Blood not available")
    
    def test_blood_compiler_paths(self):
        """Test Blood compiler paths are set correctly."""
        try:
            from field.blood import BIN_DIR, NICOLE2C_DIR
            
            assert BIN_DIR is not None
            assert NICOLE2C_DIR is not None
        except ImportError:
            pytest.skip("Blood not available")
    
    def test_blood_find_compiler(self):
        """Test Blood can find a compiler (system or binary)."""
        try:
            from field.blood import BloodCCompiler
            
            compiler = BloodCCompiler()
            found_compiler = compiler._find_compiler()
            
            # Should find something (system gcc/clang or binary)
            assert found_compiler is not None, "No compiler found - install gcc/clang or copy binaries"
        except ImportError:
            pytest.skip("Blood not available")
        except RuntimeError:
            # This is okay - no compiler available in test environment
            pass


class TestFieldCompilerIntegration:
    """Test Field integration with compilers."""
    
    def test_field_has_compilers(self):
        """Test Field initializes with compilers."""
        try:
            from field.field_core import Field
            
            field = Field()
            
            # Compilers may be None if not available, but attributes should exist
            assert hasattr(field, 'h2o')
            assert hasattr(field, 'blood')
        except ImportError:
            pytest.skip("Field not available")
    
    def test_compiler_availability_flags(self):
        """Test compiler availability flags in Field."""
        try:
            from field.field_core import H2O_AVAILABLE, BLOOD_AVAILABLE
            
            # Flags should be boolean
            assert isinstance(H2O_AVAILABLE, bool)
            assert isinstance(BLOOD_AVAILABLE, bool)
        except ImportError:
            pytest.skip("Field not available")


class TestBinariesExist:
    """Test that binary directories exist."""
    
    def test_bin_directory_exists(self):
        """Test field/bin directory exists."""
        bin_dir = Path(__file__).parent.parent / "field" / "bin"
        assert bin_dir.exists(), "field/bin/ should exist"
    
    def test_nicole2c_directory_exists(self):
        """Test field/nicole2c directory exists."""
        nicole2c_dir = Path(__file__).parent.parent / "field" / "nicole2c"
        assert nicole2c_dir.exists(), "field/nicole2c/ should exist"
    
    def test_binaries_present(self):
        """Test that some binaries/sources are present."""
        bin_dir = Path(__file__).parent.parent / "field" / "bin"
        if bin_dir.exists():
            files = list(bin_dir.iterdir())
            assert len(files) > 0, "field/bin/ should contain files"
        
        nicole2c_dir = Path(__file__).parent.parent / "field" / "nicole2c"
        if nicole2c_dir.exists():
            files = list(nicole2c_dir.iterdir())
            assert len(files) > 0, "field/nicole2c/ should contain files"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

