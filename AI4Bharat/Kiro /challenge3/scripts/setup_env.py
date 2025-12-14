#!/usr/bin/env python3
"""Script to verify environment setup and dependencies."""

import sys
import subprocess
import importlib.util
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.9+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected.")
    return True


def check_virtual_env():
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✅ Running in virtual environment.")
    else:
        print("⚠️  Not running in virtual environment. Consider using 'python -m venv venv'")
    return in_venv


def check_requirements_file():
    """Check if requirements.txt exists."""
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("✅ requirements.txt found.")
        return True
    print("❌ requirements.txt not found.")
    return False


def check_env_example():
    """Check if .env.example exists."""
    env_file = Path(".env.example")
    if env_file.exists():
        print("✅ .env.example found.")
        return True
    print("❌ .env.example not found.")
    return False


def check_project_structure():
    """Check if main project directories exist."""
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
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/ exists.")
        else:
            print(f"❌ {dir_path}/ missing.")
            all_exist = False
    
    return all_exist


def main():
    """Run all environment checks."""
    print("🔍 Checking Weather Stock Dashboard environment setup...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Requirements File", check_requirements_file),
        ("Environment Template", check_env_example),
        ("Project Structure", check_project_structure),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 All checks passed! Environment setup is complete.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the application: python main.py")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())