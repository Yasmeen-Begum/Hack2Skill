#!/usr/bin/env python3
"""
Create 100 dummy files for testing the lazy automation tool.
Creates files with extensions: .py, .txt, .java, .png, .jpeg
"""

from pathlib import Path
import random

def create_dummy_files(output_dir="test_files", total_files=100):
    """Create dummy files with various extensions."""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # File extensions to create
    extensions = ['.py', '.txt', '.java', '.png', '.jpeg']
    
    # Sample content for text files
    python_content = """#!/usr/bin/env python3
# Sample Python file
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
"""
    
    java_content = """public class Sample {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
    
    txt_content = """This is a sample text file.
It contains multiple lines of text.
Created for testing the lazy automation tool.
Line 4: Lorem ipsum dolor sit amet.
Line 5: The quick brown fox jumps over the lazy dog.
"""
    
    # PNG header (minimal valid PNG)
    png_content = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde'
        b'\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    # JPEG header (minimal valid JPEG)
    jpeg_content = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
        b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
        b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
        b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
        b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
        b'\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04'
        b'\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q'
        b'\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17'
        b'\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz'
        b'\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a'
        b'\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9'
        b'\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8'
        b'\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5'
        b'\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xff\xd9'
    )
    
    created_files = []
    
    # Create files
    for i in range(1, total_files + 1):
        # Randomly select extension
        ext = random.choice(extensions)
        filename = f"file_{i:03d}{ext}"
        filepath = output_path / filename
        
        # Write appropriate content based on extension
        if ext == '.py':
            filepath.write_text(python_content, encoding='utf-8')
        elif ext == '.java':
            filepath.write_text(java_content, encoding='utf-8')
        elif ext == '.txt':
            filepath.write_text(txt_content, encoding='utf-8')
        elif ext == '.png':
            filepath.write_bytes(png_content)
        elif ext == '.jpeg':
            filepath.write_bytes(jpeg_content)
        
        created_files.append(filename)
    
    return output_path, created_files


def main():
    """Main function."""
    print("🚀 Creating 100 dummy files...")
    print("=" * 60)
    
    output_dir, files = create_dummy_files()
    
    # Count files by extension
    ext_counts = {}
    for f in files:
        ext = Path(f).suffix
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    
    print(f"✅ Created {len(files)} files in '{output_dir}' directory")
    print("\n📊 File breakdown:")
    for ext, count in sorted(ext_counts.items()):
        print(f"   {ext}: {count} files")
    
    print("\n" + "=" * 60)
    print(f"📁 Full path: {output_dir.absolute()}")
    print("\n💡 Now you can test your automation tools with these files!")
    print("\nExamples:")
    print(f"  - Rename: Use pattern 'renamed_{{n}}{{ext}}'")
    print(f"  - Organize: Organize by 'type' to group by extension")
    print(f"  - Summarize: Get statistics on all files")
    print("\n🌐 Or use the web interface at: http://127.0.0.1:7863")


if __name__ == "__main__":
    main()
