#!/usr/bin/env python3
"""Verification script to ensure the project setup is complete and working."""

import sys
import importlib
from pathlib import Path


def test_imports():
    """Test that all main modules can be imported."""
    print("🔍 Testing module imports...")
    
    # Add current directory to Python path for testing
    import sys
    sys.path.insert(0, str(Path.cwd()))
    
    modules_to_test = [
        ("main", "main.py"),
        ("config.settings", "config/settings.py"),
        ("weather_stock_dashboard.api.routes", "weather_stock_dashboard/api/routes.py"),
    ]
    
    success = True
    for module_name, file_path in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} imported successfully")
        except Exception as e:
            print(f"❌ Failed to import {module_name}: {e}")
            success = False
    
    return success


def test_fastapi_app():
    """Test that FastAPI app can be created."""
    print("\n🔍 Testing FastAPI application...")
    
    try:
        # Add current directory to Python path
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from main import app
        print("✅ FastAPI app created successfully")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/api/status"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"❌ Route {route} not found")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False


def test_settings():
    """Test that settings can be loaded."""
    print("\n🔍 Testing configuration settings...")
    
    try:
        # Add current directory to Python path
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from config.settings import settings
        print("✅ Settings loaded successfully")
        
        # Test some basic settings
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ App version: {settings.app_version}")
        print(f"✅ API host: {settings.api_host}")
        print(f"✅ API port: {settings.api_port}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return False


def test_project_structure():
    """Test that all required files and directories exist."""
    print("\n🔍 Testing project structure...")
    
    required_items = [
        # Main files
        ("main.py", "file"),
        ("requirements.txt", "file"),
        ("pyproject.toml", "file"),
        (".env.example", "file"),
        (".gitignore", "file"),
        ("README.md", "file"),
        ("Makefile", "file"),
        
        # Directories
        ("weather_stock_dashboard", "dir"),
        ("config", "dir"),
        ("tests", "dir"),
        ("scripts", "dir"),
        
        # Package directories
        ("weather_stock_dashboard/models", "dir"),
        ("weather_stock_dashboard/services", "dir"),
        ("weather_stock_dashboard/agents", "dir"),
        ("weather_stock_dashboard/api", "dir"),
        ("weather_stock_dashboard/mcp_servers", "dir"),
        ("weather_stock_dashboard/ui", "dir"),
        ("weather_stock_dashboard/utils", "dir"),
    ]
    
    success = True
    for item_path, item_type in required_items:
        path = Path(item_path)
        if item_type == "file" and path.is_file():
            print(f"✅ {item_path} (file)")
        elif item_type == "dir" and path.is_dir():
            print(f"✅ {item_path}/ (directory)")
        else:
            print(f"❌ {item_path} missing or wrong type")
            success = False
    
    return success


def main():
    """Run all verification tests."""
    print("🚀 Verifying Weather Stock Dashboard setup...\n")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Configuration Settings", test_settings),
        ("FastAPI Application", test_fastapi_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        results.append(test_func())
    
    print("\n" + "="*60)
    if all(results):
        print("🎉 All verification tests passed!")
        print("\n✨ Weather Stock Dashboard is ready for development!")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start development with task 2: Implement core data models")
        return 0
    else:
        print("❌ Some verification tests failed.")
        print("Please review the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())