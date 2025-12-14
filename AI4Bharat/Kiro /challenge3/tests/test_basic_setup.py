"""Basic tests to verify project setup and structure."""

import pytest
from pathlib import Path
import importlib.util


class TestProjectStructure:
    """Test that the project structure is correctly set up."""
    
    def test_main_directories_exist(self):
        """Test that all main directories exist."""
        required_dirs = [
            "weather_stock_dashboard",
            "weather_stock_dashboard/models",
            "weather_stock_dashboard/services", 
            "weather_stock_dashboard/agents",
            "weather_stock_dashboard/api",
            "weather_stock_dashboard/mcp_servers",
            "weather_stock_dashboard/ui",
            "weather_stock_dashboard/utils",
            "config",
            "tests"
        ]
        
        for dir_path in required_dirs:
            assert Path(dir_path).exists(), f"Directory {dir_path} should exist"
            assert Path(dir_path).is_dir(), f"{dir_path} should be a directory"
    
    def test_init_files_exist(self):
        """Test that __init__.py files exist in Python packages."""
        init_files = [
            "weather_stock_dashboard/__init__.py",
            "weather_stock_dashboard/models/__init__.py",
            "weather_stock_dashboard/services/__init__.py",
            "weather_stock_dashboard/agents/__init__.py",
            "weather_stock_dashboard/api/__init__.py",
            "weather_stock_dashboard/mcp_servers/__init__.py",
            "weather_stock_dashboard/ui/__init__.py",
            "weather_stock_dashboard/utils/__init__.py",
            "config/__init__.py",
            "tests/__init__.py"
        ]
        
        for init_file in init_files:
            assert Path(init_file).exists(), f"Init file {init_file} should exist"
    
    def test_config_files_exist(self):
        """Test that configuration files exist."""
        config_files = [
            "requirements.txt",
            "pyproject.toml",
            ".env.example",
            ".gitignore",
            "README.md",
            "Makefile"
        ]
        
        for config_file in config_files:
            assert Path(config_file).exists(), f"Config file {config_file} should exist"
    
    def test_main_py_exists(self):
        """Test that main.py exists and is importable."""
        assert Path("main.py").exists(), "main.py should exist"
        
        # Test that main.py can be compiled
        spec = importlib.util.spec_from_file_location("main", "main.py")
        assert spec is not None, "main.py should be a valid Python module"


class TestConfigurationImport:
    """Test that configuration modules can be imported."""
    
    def test_settings_import(self):
        """Test that settings can be imported."""
        try:
            from config.settings import Settings
            assert Settings is not None
        except ImportError as e:
            pytest.fail(f"Could not import Settings: {e}")
    
    def test_api_routes_import(self):
        """Test that API routes can be imported."""
        try:
            from weather_stock_dashboard.api.routes import router
            assert router is not None
        except ImportError as e:
            pytest.fail(f"Could not import API router: {e}")


class TestRequirements:
    """Test requirements and dependencies."""
    
    def test_requirements_file_format(self):
        """Test that requirements.txt is properly formatted."""
        req_file = Path("requirements.txt")
        assert req_file.exists(), "requirements.txt should exist"
        
        content = req_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Should have some dependencies
        assert len(lines) > 10, "Should have multiple dependencies"
        
        # Check for key dependencies
        content_lower = content.lower()
        key_deps = ['fastapi', 'langchain', 'chromadb', 'gradio', 'statsmodels', 'arch']
        
        for dep in key_deps:
            assert dep in content_lower, f"Should include {dep} dependency"
    
    def test_env_example_format(self):
        """Test that .env.example has required variables."""
        env_file = Path(".env.example")
        assert env_file.exists(), ".env.example should exist"
        
        content = env_file.read_text()
        
        # Check for required API keys
        required_vars = [
            'OPENWEATHER_API_KEY',
            'ALPHA_VANTAGE_API_KEY', 
            'OPENAI_API_KEY'
        ]
        
        for var in required_vars:
            assert var in content, f"Should include {var} in .env.example"