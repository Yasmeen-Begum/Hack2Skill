#!/usr/bin/env python3
"""
Demo script to showcase the Lazy Automation Tool web interface.

This script creates sample files and launches the web interface for demonstration.
"""

import tempfile
import shutil
from pathlib import Path
import json
import csv
from datetime import datetime, timedelta

def create_demo_files():
    """Create a demo directory with various file types for testing."""
    # Create a demo directory in the current folder
    demo_dir = Path("demo_files")
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    demo_dir.mkdir()
    
    print(f"📁 Creating demo files in: {demo_dir.absolute()}")
    
    # Create various file types for organization demo
    files_created = []
    
    # Text files
    for i in range(1, 4):
        file_path = demo_dir / f"document_{i}.txt"
        file_path.write_text(f"This is document number {i}.\nIt contains some sample text for analysis.\nLine count: 3\nWord count: varies")
        files_created.append(str(file_path))
    
    # Images (empty files for demo)
    for i in range(1, 3):
        file_path = demo_dir / f"photo_{i}.jpg"
        file_path.write_text("fake image content")
        files_created.append(str(file_path))
    
    # Documents
    for i in range(1, 3):
        file_path = demo_dir / f"report_{i}.pdf"
        file_path.write_text("fake pdf content")
        files_created.append(str(file_path))
    
    # Code files
    code_content = '''def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return "success"

if __name__ == "__main__":
    hello_world()
'''
    for i in range(1, 3):
        file_path = demo_dir / f"script_{i}.py"
        file_path.write_text(code_content)
        files_created.append(str(file_path))
    
    # JSON file
    json_data = {
        "name": "Sample Data",
        "version": "1.0",
        "items": [
            {"id": 1, "name": "Item 1", "active": True},
            {"id": 2, "name": "Item 2", "active": False},
            {"id": 3, "name": "Item 3", "active": True}
        ],
        "metadata": {
            "created": datetime.now().isoformat(),
            "author": "Demo Script"
        }
    }
    json_file = demo_dir / "data.json"
    json_file.write_text(json.dumps(json_data, indent=2))
    files_created.append(str(json_file))
    
    # CSV file
    csv_file = demo_dir / "sample_data.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Age', 'City', 'Score'])
        writer.writerow(['Alice', '25', 'New York', '95'])
        writer.writerow(['Bob', '30', 'San Francisco', '87'])
        writer.writerow(['Charlie', '35', 'Chicago', '92'])
        writer.writerow(['Diana', '28', 'Boston', '98'])
    files_created.append(str(csv_file))
    
    # Create files with different dates (modify timestamps)
    import os
    base_time = datetime.now()
    for i, file_path in enumerate(files_created):
        # Vary the modification times
        mod_time = base_time - timedelta(days=i * 2)
        timestamp = mod_time.timestamp()
        os.utime(file_path, (timestamp, timestamp))
    
    print(f"✅ Created {len(files_created)} demo files:")
    for file_path in files_created:
        print(f"   - {Path(file_path).name}")
    
    return str(demo_dir.absolute())

def print_demo_instructions(demo_dir):
    """Print instructions for using the demo."""
    print("\n" + "="*60)
    print("🚀 LAZY AUTOMATION TOOL - WEB INTERFACE DEMO")
    print("="*60)
    print(f"📁 Demo directory: {demo_dir}")
    print("\n📝 Try these operations in the web interface:")
    print("\n1. RENAME TAB:")
    print(f"   Directory: {demo_dir}")
    print("   Pattern: renamed_{n}.txt")
    print("   Extensions: .txt")
    print("   ✅ Enable Preview Mode first!")
    
    print("\n2. ORGANIZE TAB:")
    print(f"   Directory: {demo_dir}")
    print("   Rule: type")
    print("   Conflict Strategy: skip")
    print("   ✅ Enable Preview Mode first!")
    
    print("\n3. SUMMARIZE TAB:")
    print(f"   Directory: {demo_dir}")
    print("   Extensions: .txt,.json,.csv")
    print(f"   Output File: {demo_dir}/summary_report.txt")
    
    print("\n💡 Tips:")
    print("   - Always use Preview Mode first to see changes")
    print("   - Try different patterns like: photo_{n}_{name}.jpg")
    print("   - Organize by 'date' to see date-based grouping")
    print("   - Leave extensions empty to process all files")
    
    print("\n🌐 The web interface will open in your browser automatically.")
    print("   If not, navigate to: http://localhost:7860")
    print("\n⏹️  Press Ctrl+C in this terminal to stop the server")
    print("="*60)

def main():
    """Main demo function."""
    print("🎬 Setting up Lazy Automation Tool Demo...")
    
    # Create demo files
    demo_dir = create_demo_files()
    
    # Print instructions
    print_demo_instructions(demo_dir)
    
    # Launch the web interface
    print("\n🚀 Launching web interface...")
    try:
        from lazy_automation.web_interface import WebInterface
        
        web_interface = WebInterface()
        web_interface.launch(
            share=False,
            server_name="127.0.0.1",
            server_port=7860,
            show_error=True,
            quiet=False
        )
    except ImportError:
        print("❌ Error: lazy_automation package not found.")
        print("   Please install it first: pip install -e .")
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user.")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")
    finally:
        # Cleanup option
        print(f"\n🧹 Demo files are in: {demo_dir}")
        print("   You can delete this directory when done with the demo.")

if __name__ == "__main__":
    main()