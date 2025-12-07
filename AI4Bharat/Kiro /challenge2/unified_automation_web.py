#!/usr/bin/env python3
"""
File Automation Web Interface with Gradio

Bulk rename and organize files with ease.
"""

import gradio as gr
from pathlib import Path
from typing import Tuple, List
import io
import shutil
import tempfile
import os
import pandas as pd

# Import file automation components
from lazy_automation.coordinator import TaskCoordinator
from lazy_automation.reporting import Reporter


class FileAutomationWeb:
    """Web interface for file automation (rename and organize)."""
    
    def __init__(self):
        """Initialize the interface."""
        self.file_coordinator = TaskCoordinator()
        
        # Bulk file renamer
        self.uploaded_files = []
        self.temp_dir = None
    
    def handle_file_organize(self, directory: str, rule_type: str,
                            conflict_strategy: str, dry_run: bool) -> str:
        """Handle file organization operation."""
        try:
            if not directory or not directory.strip():
                return "❌ Error: Directory path is required"
            
            dir_path = Path(directory.strip())
            if not dir_path.exists():
                return f"❌ Error: Directory not found: {directory}"
            
            if not dir_path.is_dir():
                return f"❌ Error: Not a directory: {directory}"
            
            # Prepare options
            options = {
                'rule_type': rule_type,
                'conflict_strategy': conflict_strategy
            }
            
            # Capture output
            output_buffer = io.StringIO()
            reporter = Reporter(verbose=True, output=output_buffer)
            coordinator = TaskCoordinator(reporter=reporter)
            
            # Execute task
            result = coordinator.execute_task(
                task_type='organize',
                directory=str(dir_path),
                options=options,
                dry_run=dry_run
            )
            
            output = output_buffer.getvalue()
            
            # Add summary
            if dry_run:
                summary = f"\n✅ Preview Complete\n"
                summary += f"📁 {result.success_count} file(s) would be organized\n"
                if result.failure_count > 0:
                    summary += f"⚠️ {result.failure_count} operation(s) would fail\n"
            else:
                summary = f"\n✅ Organization Complete\n"
                summary += f"📁 {result.success_count} file(s) organized successfully\n"
                if result.failure_count > 0:
                    summary += f"❌ {result.failure_count} operation(s) failed\n"
            
            return summary + "\n" + output
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== BULK FILE RENAMER METHODS ====================
    
    def process_uploaded_files(self, files: List) -> Tuple[pd.DataFrame, str]:
        """Process uploaded files and create editable table."""
        if not files:
            return (pd.DataFrame(), "❌ No files uploaded. Please upload files first.")
        
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        self.temp_dir = tempfile.mkdtemp()
        self.uploaded_files = []
        
        file_data = []
        for i, file in enumerate(files, 1):
            if file is None:
                continue
            
            original_name = Path(file.name).name
            temp_path = os.path.join(self.temp_dir, original_name)
            shutil.copy2(file.name, temp_path)
            self.uploaded_files.append(temp_path)
            
            file_data.append({
                'No.': i,
                'Original Name': original_name,
                'New Name': original_name,
                'Size': self._format_size(os.path.getsize(temp_path)),
                'Extension': Path(original_name).suffix
            })
        
        if not file_data:
            return (pd.DataFrame(), "❌ No valid files found.")
        
        df = pd.DataFrame(file_data)
        status = f"✅ Uploaded {len(file_data)} file(s)\n\n"
        status += "📝 Edit the 'New Name' column to rename files\n"
        status += "🔄 Click 'Apply Pattern' to use automatic naming\n"
        status += "✅ Click 'Rename Files' when ready"
        
        return (df, status)
    
    def apply_bulk_pattern(self, df: pd.DataFrame, pattern: str, start_number: int) -> Tuple[pd.DataFrame, str]:
        """Apply naming pattern to all files."""
        if df is None or df.empty:
            return (df, "❌ No files to apply pattern to")
        
        if not pattern or not pattern.strip():
            return (df, "❌ Please enter a pattern")
        
        pattern = pattern.strip()
        
        for idx, row in df.iterrows():
            original_name = row['Original Name']
            original_path = Path(original_name)
            
            new_name = pattern
            new_name = new_name.replace('{n}', str(start_number + idx))
            new_name = new_name.replace('{name}', original_path.stem)
            new_name = new_name.replace('{ext}', original_path.suffix.lstrip('.'))
            
            pattern_has_extension = '.' in new_name or '{ext}' in pattern
            
            if not pattern_has_extension and original_path.suffix:
                new_name = new_name + original_path.suffix
            
            df.at[idx, 'New Name'] = new_name
        
        status = f"✅ Pattern applied to {len(df)} file(s)\n\n"
        status += f"Pattern: {pattern}\n"
        status += "📝 You can still edit individual names if needed"
        
        return (df, status)
    
    def rename_bulk_files(self, df: pd.DataFrame, output_dir: str) -> str:
        """Rename files based on the DataFrame."""
        if df is None or df.empty:
            return "❌ No files to rename"
        
        if not output_dir or not output_dir.strip():
            return "❌ Please specify output directory"
        
        output_path = Path(output_dir.strip())
        output_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                original_name = row['Original Name']
                new_name = row['New Name']
                
                if not new_name or not new_name.strip():
                    errors.append(f"Row {idx + 1}: New name is empty")
                    continue
                
                original_path = os.path.join(self.temp_dir, original_name)
                
                if not os.path.exists(original_path):
                    errors.append(f"Row {idx + 1}: Original file not found")
                    continue
                
                new_path = output_path / new_name.strip()
                
                if new_path.exists():
                    errors.append(f"Row {idx + 1}: '{new_name}' already exists")
                    continue
                
                shutil.copy2(original_path, new_path)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        status = "=" * 60 + "\n"
        status += "📊 RENAME RESULTS\n"
        status += "=" * 60 + "\n\n"
        status += f"✅ Successfully renamed: {success_count} file(s)\n"
        status += f"❌ Failed: {len(errors)} file(s)\n"
        status += f"📁 Output directory: {output_path}\n\n"
        
        if errors:
            status += "⚠️ Errors:\n"
            for error in errors[:10]:
                status += f"   • {error}\n"
            if len(errors) > 10:
                status += f"   ... and {len(errors) - 10} more errors\n"
        
        if success_count > 0:
            status += f"\n🎉 {success_count} file(s) renamed successfully!\n"
        
        return status
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def create_interface():
    """Create the Gradio interface."""
    
    app = FileAutomationWeb()
    
    with gr.Blocks(title="File Automation Tool") as interface:
        gr.Markdown("# 🚀 File Automation Tool")
        gr.Markdown("""
        **Bulk rename and organize files with ease**
        
        Stop wasting time on boring file management tasks!
        """)
        
        with gr.Tabs():
            # ==================== ORGANIZE FILES TAB ====================
            
            with gr.Tab("📁 Organize Files"):
                gr.Markdown("### Organize Files into Folders")
                gr.Markdown("Automatically organize files into subdirectories based on type, date, or name (alphabetically).")
                
                with gr.Row():
                    with gr.Column():
                        organize_dir = gr.Textbox(
                            label="Directory Path",
                            placeholder="C:\\Users\\YourName\\Downloads",
                            info="Full path to the directory to organize"
                        )
                        organize_rule = gr.Radio(
                            choices=["type", "date", "name"],
                            label="Organization Rule",
                            value="type",
                            info="Organize by file type, modification date, or alphabetically by name"
                        )
                        organize_conflict = gr.Radio(
                            choices=["skip", "overwrite", "rename"],
                            label="Conflict Strategy",
                            value="skip",
                            info="How to handle files that already exist at destination"
                        )
                        organize_dry_run = gr.Checkbox(
                            label="Preview Mode (Dry Run)",
                            value=True,
                            info="Show changes without executing them"
                        )
                        organize_btn = gr.Button("Execute Organization", variant="primary", size="lg")
                    
                    with gr.Column():
                        organize_output = gr.Textbox(
                            label="Results",
                            lines=20,
                            max_lines=30,
                            interactive=False
                        )
                
                organize_btn.click(
                    fn=app.handle_file_organize,
                    inputs=[organize_dir, organize_rule, organize_conflict, organize_dry_run],
                    outputs=organize_output
                )
            
            # ==================== BULK FILE RENAMER TAB ====================
            
            with gr.Tab("📤 Bulk Upload & Rename"):
                gr.Markdown("### Upload Multiple Files & Rename")
                gr.Markdown("Upload 100+ files, edit names in a table, and rename them all at once!")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📤 Step 1: Upload Files")
                        
                        file_upload = gr.File(
                            label="Upload Files (Multiple)",
                            file_count="multiple",
                            file_types=None,
                            type="filepath"
                        )
                        
                        upload_btn = gr.Button("📋 Load Files", variant="primary", size="lg")
                        
                        gr.Markdown("---")
                        gr.Markdown("#### 🔄 Step 2: Apply Pattern (Optional)")
                        
                        bulk_pattern_input = gr.Textbox(
                            label="Naming Pattern",
                            placeholder="e.g., file_{n}.txt or photo_{n}_{name}",
                            info="Use {n} for number, {name} for original, {ext} for extension"
                        )
                        
                        bulk_start_number = gr.Number(
                            label="Start Number",
                            value=1,
                            precision=0
                        )
                        
                        bulk_pattern_btn = gr.Button("🔄 Apply Pattern", variant="secondary")
                        
                        gr.Markdown("---")
                        gr.Markdown("#### ✅ Step 3: Rename Files")
                        
                        bulk_output_dir = gr.Textbox(
                            label="Output Directory",
                            placeholder="C:\\Users\\YourName\\Desktop\\renamed_files",
                            info="Where to save renamed files"
                        )
                        
                        bulk_rename_btn = gr.Button("✅ Rename All Files", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("#### 📊 Files Preview & Edit")
                        
                        bulk_status_output = gr.Textbox(
                            label="Status",
                            lines=5,
                            interactive=False
                        )
                        
                        bulk_files_table = gr.Dataframe(
                            label="Files (Edit 'New Name' column to rename)",
                            headers=['No.', 'Original Name', 'New Name', 'Size', 'Extension'],
                            datatype=['number', 'str', 'str', 'str', 'str'],
                            interactive=True,
                            wrap=True
                        )
                        
                        bulk_result_output = gr.Textbox(
                            label="Rename Results",
                            lines=10,
                            interactive=False
                        )
                
                gr.Markdown("""
                ---
                ### 💡 Pattern Examples
                
                - `file_{n}.txt` → file_1.txt, file_2.txt (changes extension to .txt)
                - `photo_{n}_{name}.jpg` → photo_1_vacation.jpg, photo_2_beach.jpg
                - `doc_{n}.{ext}` → doc_1.pdf, doc_2.docx (keeps original extension)
                - `renamed_{n}` → renamed_1, renamed_2 (no extension)
                
                **Placeholders:**
                - `{n}` - Sequential number
                - `{name}` - Original filename (without extension)
                - `{ext}` - File extension (without dot)
                """)
                
                # Event handlers for bulk renamer
                upload_btn.click(
                    fn=app.process_uploaded_files,
                    inputs=file_upload,
                    outputs=[bulk_files_table, bulk_status_output]
                )
                
                bulk_pattern_btn.click(
                    fn=app.apply_bulk_pattern,
                    inputs=[bulk_files_table, bulk_pattern_input, bulk_start_number],
                    outputs=[bulk_files_table, bulk_status_output]
                )
                
                bulk_rename_btn.click(
                    fn=app.rename_bulk_files,
                    inputs=[bulk_files_table, bulk_output_dir],
                    outputs=bulk_result_output
                )
        
        gr.Markdown("""
        ---
        **File Automation Tool** - Bulk rename and organize files! 🚀✨
        """)
    
    return interface


def main():
    """Main function to launch the interface."""
    print("🚀 Launching File Automation Tool...")
    print("=" * 60)
    print("Features:")
    print("  📁 Organize Files")
    print("  📤 Bulk Upload & Rename")
    print("=" * 60)
    print("Access at: http://localhost:7863")
    print("=" * 60)
    
    interface = create_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
