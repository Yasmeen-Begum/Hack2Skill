#!/usr/bin/env python3
"""Installation script for Weather Stock Dashboard."""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def create_virtual_environment():
    """Create a Python virtual environment."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def get_activation_command():
    """Get the appropriate activation command for the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Install Python dependencies."""
    if platform.system() == "Windows":
        pip_command = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_command = "venv/bin/pip install -r requirements.txt"
    
    return run_command(pip_command, "Installing dependencies")


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists.")
        return True
    
    if env_example.exists():
        try:
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from template.")
            print("⚠️  Please edit .env file with your API keys.")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example not found.")
        return False


def main():
    """Run the installation process."""
    print("🚀 Installing Weather Stock Dashboard...\n")
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found. Please run this script from the project root.")
        return 1
    
    steps = [
        ("Create Virtual Environment", create_virtual_environment),
        ("Install Dependencies", install_dependencies),
        ("Create Environment File", create_env_file),
    ]
    
    for name, step_func in steps:
        print(f"\n📋 {name}:")
        if not step_func():
            print(f"❌ Installation failed at step: {name}")
            return 1
    
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("\nNext steps:")
    print(f"1. Activate virtual environment: {get_activation_command()}")
    print("2. Edit .env file with your API keys")
    print("3. Run the application: python main.py")
    print("4. Visit http://localhost:8000 to see the API")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())