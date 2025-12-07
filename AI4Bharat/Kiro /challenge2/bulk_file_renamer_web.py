#!/usr/bin/env python3
"""
Bulk File Renamer Web Interface with Gradio

Upload multiple files, see them side-by-side, edit names, and rename all at once.
"""

import gradio as gr
from pathlib import Path
import shutil
import tempfile
import os
from typing import List, Tuple, Dict
import pandas as pd


class BulkFileRenamer:
    """Bulk file renaming with side-by-side editing."""
    
    def __init__(self):
        """Initialize the renamer."""
        self.uploaded_files = []
        self.temp_dir = None
        self.file_mapping = {}
    
    def process_uploaded_files(self, files: List) -> Tuple[pd.DataFrame, str]:
        """
        Process uploaded files and create editable table.
        
        Args:
            files: List of uploaded file objects
            
        Returns:
            Tuple of (DataFrame with original and new names, status message)
        """
        if not files:
            return (pd.DataFrame(), "❌ No files uploaded. Please upload files first.")
        
        # Create temporary directory for uploaded files
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        self.temp_dir = tempfile.mkdtemp()
        self.uploaded_files = []
        self.file_mapping = {}
        
        # Process each uploaded file
        file_data = []
        for i, file in enumerate(files, 1):
            if file is None:
                continue
            
            # Get original filename
            original_name = Path(file.name).name
            
            # Copy file to temp directory
            temp_path = os.path.join(self.temp_dir, original_name)
            shutil.copy2(file.name, temp_path)
            
            self.uploaded_files.append(temp_path)
            
            # Add to table data
            file_data.append({
                'No.': i,
                'Original Name': original_name,
                'New Name': original_name,  # Default to original name
                'Size': self._format_size(os.path.getsize(temp_path)),
                'Extension': Path(original_name).suffix
            })
        
        if not file_data:
            return (pd.DataFrame(), "❌ No valid files found.")
        
        df = pd.DataFrame(file_data)
        
        status = f"✅ Uploaded {len(file_data)} file(s)\n\n"
        status += "📝 Edit the 'New Name' column to rename files\n"
        status += "💡 Tip: You can copy-paste from Excel or edit directly\n"
        status += "🔄 Click 'Apply Pattern' to use automatic naming\n"
        status += "✅ Click 'Rename Files' when ready"
        
        return (df, status)
    
    def apply_pattern(self, df: pd.DataFrame, pattern: str, 
                     start_number: int) -> Tuple[pd.DataFrame, str]:
        """
        Apply naming pattern to all files.
        
        Args:
            df: Current DataFrame
            pattern: Pattern to apply (e.g., "file_{n}")
            start_number: Starting number for {n}
            
        Returns:
            Tuple of (updated DataFrame, status message)
        """
        if df is None or df.empty:
            return (df, "❌ No files to apply pattern to")
        
        if not pattern or not pattern.strip():
            return (df, "❌ Please enter a pattern")
        
        pattern = pattern.strip()
        
        # Apply pattern to each file
        for idx, row in df.iterrows():
            original_name = row['Original Name']
            original_path = Path(original_name)
            
            # Replace placeholders
            new_name = pattern
            new_name = new_name.replace('{n}', str(start_number + idx))
            new_name = new_name.replace('{name}', original_path.stem)
            new_name = new_name.replace('{ext}', original_path.suffix.lstrip('.'))
            
            # Check if pattern already includes an extension
            pattern_has_extension = '.' in new_name or '{ext}' in pattern
            
            # Only add extension if pattern doesn't already have one
            if not pattern_has_extension and original_path.suffix:
                new_name = new_name + original_path.suffix
            
            df.at[idx, 'New Name'] = new_name
        
        status = f"✅ Pattern applied to {len(df)} file(s)\n\n"
        status += f"Pattern: {pattern}\n"
        status += f"Starting number: {start_number}\n\n"
        status += "📝 You can still edit individual names if needed\n"
        status += "✅ Click 'Rename Files' to apply changes"
        
        return (df, status)
    
    def rename_files(self, df: pd.DataFrame, output_dir: str) -> Tuple[str, List]:
        """
        Rename files based on the DataFrame.
        
        Args:
            df: DataFrame with original and new names
            output_dir: Directory to save renamed files
            
        Returns:
            Tuple of (status message, list of renamed file paths)
        """
        if df is None or df.empty:
            return ("❌ No files to rename", [])
        
        if not output_dir or not output_dir.strip():
            return ("❌ Please specify output directory", [])
        
        # Create output directory
        output_path = Path(output_dir.strip())
        output_path.mkdir(parents=True, exist_ok=True)
        
        renamed_files = []
        success_count = 0
        errors = []
        
        # Rename each file
        for idx, row in df.iterrows():
            try:
                original_name = row['Original Name']
                new_name = row['New Name']
                
                if not new_name or not new_name.strip():
                    errors.append(f"Row {idx + 1}: New name is empty")
                    continue
                
                # Find original file in temp directory
                original_path = os.path.join(self.temp_dir, original_name)
                
                if not os.path.exists(original_path):
                    errors.append(f"Row {idx + 1}: Original file not found")
                    continue
                
                # Create new file path
                new_path = output_path / new_name.strip()
                
                # Check if file already exists
                if new_path.exists():
                    errors.append(f"Row {idx + 1}: '{new_name}' already exists")
                    continue
                
                # Copy and rename file
                shutil.copy2(original_path, new_path)
                renamed_files.append(str(new_path))
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        # Build status message
        status = "=" * 60 + "\n"
        status += "📊 RENAME RESULTS\n"
        status += "=" * 60 + "\n\n"
        status += f"✅ Successfully renamed: {success_count} file(s)\n"
        status += f"❌ Failed: {len(errors)} file(s)\n"
        status += f"📁 Output directory: {output_path}\n\n"
        
        if errors:
            status += "⚠️ Errors:\n"
            for error in errors[:10]:  # Show first 10 errors
                status += f"   • {error}\n"
            if len(errors) > 10:
                status += f"   ... and {len(errors) - 10} more errors\n"
        
        status += "\n" + "=" * 60 + "\n"
        
        if success_count > 0:
            status += f"\n🎉 {success_count} file(s) renamed successfully!\n"
            status += f"📂 Check: {output_path}\n"
        
        return (status, renamed_files)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def create_interface():
    """Create the Gradio interface."""
    
    renamer = BulkFileRenamer()
    
    with gr.Blocks(title="Bulk File Renamer") as interface:
        gr.Markdown("# 📁 Bulk File Renamer")
        gr.Markdown("""
        Upload multiple files, edit names side-by-side, and rename them all at once!
        
        **Features**: Upload 100+ files • Side-by-side editing • Pattern-based naming • Bulk rename
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Step 1: Upload Files")
                
                file_upload = gr.File(
                    label="Upload Files (Multiple)",
                    file_count="multiple",
                    file_types=None,
                    type="filepath"
                )
                
                upload_btn = gr.Button("📋 Load Files", variant="primary", size="lg")
                
                gr.Markdown("---")
                gr.Markdown("### 🔄 Step 2: Apply Pattern (Optional)")
                
                pattern_input = gr.Textbox(
                    label="Naming Pattern",
                    placeholder="e.g., file_{n} or photo_{n}_{name}",
                    info="Use {n} for number, {name} for original name, {ext} for extension"
                )
                
                start_number = gr.Number(
                    label="Start Number",
                    value=1,
                    precision=0,
                    info="Starting number for {n}"
                )
                
                pattern_btn = gr.Button("🔄 Apply Pattern", variant="secondary")
                
                gr.Markdown("---")
                gr.Markdown("### ✅ Step 3: Rename Files")
                
                output_dir = gr.Textbox(
                    label="Output Directory",
                    placeholder="C:/Users/YourName/Desktop/renamed_files",
                    info="Where to save renamed files"
                )
                
                rename_btn = gr.Button("✅ Rename All Files", variant="primary", size="lg")
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Files Preview & Edit")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=5,
                    interactive=False
                )
                
                files_table = gr.Dataframe(
                    label="Files (Edit 'New Name' column to rename)",
                    headers=['No.', 'Original Name', 'New Name', 'Size', 'Extension'],
                    datatype=['number', 'str', 'str', 'str', 'str'],
                    col_count=(5, 'fixed'),
                    interactive=True,
                    wrap=True
                )
                
                result_output = gr.Textbox(
                    label="Rename Results",
                    lines=10,
                    interactive=False,
                    visible=False
                )
                
                download_files = gr.File(
                    label="Download Renamed Files",
                    file_count="multiple",
                    visible=False
                )
        
        gr.Markdown("""
        ---
        ### 💡 Quick Tips
        
        **Pattern Examples:**
        - `file_{n}` → file_1.jpg, file_2.jpg, file_3.jpg
        - `photo_{n}_{name}` → photo_1_vacation.jpg, photo_2_beach.jpg
        - `doc_{n}.{ext}` → doc_1.pdf, doc_2.docx
        - `2024_{n}_{name}` → 2024_1_report.pdf, 2024_2_invoice.pdf
        
        **Placeholders:**
        - `{n}` - Sequential number (1, 2, 3...)
        - `{name}` - Original filename (without extension)
        - `{ext}` - File extension (without dot)
        
        **Editing:**
        - Click any cell in 'New Name' column to edit
        - Copy-paste from Excel/Sheets
        - Edit multiple files at once
        """)
        
        # Event handlers
        upload_btn.click(
            fn=renamer.process_uploaded_files,
            inputs=file_upload,
            outputs=[files_table, status_output]
        )
        
        pattern_btn.click(
            fn=renamer.apply_pattern,
            inputs=[files_table, pattern_input, start_number],
            outputs=[files_table, status_output]
        )
        
        rename_btn.click(
            fn=renamer.rename_files,
            inputs=[files_table, output_dir],
            outputs=[result_output, download_files]
        ).then(
            fn=lambda: (gr.update(visible=True), gr.update(visible=True)),
            outputs=[result_output, download_files]
        )
    
    return interface


def main():
    """Main function to launch the interface."""
    print("🚀 Launching Bulk File Renamer...")
    print("=" * 60)
    print("Upload 100+ files and rename them all at once!")
    print("Access at: http://localhost:7863")
    print("=" * 60)
    
    interface = create_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7864,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
