"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
from lazy_automation.coordinator import TaskCoordinator
from lazy_automation.reporting import Reporter
from lazy_automation.cli.main import parse_arguments, execute_task
import io
import sys


class TestEndToEndRenameWorkflow:
    """Test end-to-end rename workflow."""
    
    def test_rename_workflow_with_sequential_numbering(self, temp_dir):
        """Test complete rename workflow with sequential numbering pattern."""
        # Create test files
        files = []
        for i in range(5):
            file_path = temp_dir / f"old_file_{i}.txt"
            file_path.write_text(f"Content {i}")
            files.append(file_path)
        
        # Execute rename task
        coordinator = TaskCoordinator()
        options = {'pattern': 'new_{n}.txt'}
        
        result = coordinator.execute_task('rename', str(temp_dir), options, dry_run=False)
        
        # Verify results
        assert result.success_count == 5
        assert result.failure_count == 0
        assert len(result.errors) == 0
        
        # Verify files were renamed
        for i in range(1, 6):
            new_file = temp_dir / f"new_{i}.txt"
            assert new_file.exists()
            assert new_file.read_text() == f"Content {i-1}"
        
        # Verify old files don't exist
        for old_file in files:
            assert not old_file.exists()
    
    def test_rename_workflow_with_extension_filter(self, temp_dir):
        """Test rename workflow with extension filtering."""
        # Create mixed file types
        (temp_dir / "file1.txt").write_text("Text 1")
        (temp_dir / "file2.txt").write_text("Text 2")
        (temp_dir / "file3.pdf").write_text("PDF content")
        (temp_dir / "file4.jpg").write_text("Image data")
        
        # Execute rename task with .txt filter
        coordinator = TaskCoordinator()
        options = {'pattern': 'renamed_{n}.txt', 'extensions': ['.txt']}
        
        result = coordinator.execute_task('rename', str(temp_dir), options, dry_run=False)
        
        # Verify only .txt files were renamed
        assert result.success_count == 2
        assert (temp_dir / "renamed_1.txt").exists()
        assert (temp_dir / "renamed_2.txt").exists()
        
        # Verify other files unchanged
        assert (temp_dir / "file3.pdf").exists()
        assert (temp_dir / "file4.jpg").exists()
    
    def test_rename_workflow_detects_conflicts(self, temp_dir):
        """Test that rename workflow detects and prevents conflicts."""
        # Create files that would conflict
        (temp_dir / "file1.txt").write_text("Content 1")
        (temp_dir / "file2.txt").write_text("Content 2")
        
        # Try to rename all to same name (no numbering)
        coordinator = TaskCoordinator()
        options = {'pattern': 'same_name.txt'}
        
        # Should raise ValueError due to conflicts
        with pytest.raises(ValueError, match="duplicate filenames"):
            coordinator.execute_task('rename', str(temp_dir), options, dry_run=False)


class TestEndToEndOrganizeWorkflow:
    """Test end-to-end organize workflow."""
    
    def test_organize_by_type_workflow(self, temp_dir):
        """Test complete organize workflow by file type."""
        # Create mixed file types
        (temp_dir / "doc1.txt").write_text("Text")
        (temp_dir / "doc2.pdf").write_text("PDF")
        (temp_dir / "image1.jpg").write_text("Image")
        (temp_dir / "image2.png").write_text("Image")
        (temp_dir / "video.mp4").write_text("Video")
        (temp_dir / "unknown.xyz").write_text("Unknown")
        
        # Execute organize task
        coordinator = TaskCoordinator()
        options = {'rule_type': 'type', 'conflict_strategy': 'skip'}
        
        result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=False)
        
        # Verify results
        assert result.success_count == 6
        assert result.failure_count == 0
        
        # Verify files were organized into correct subdirectories
        assert (temp_dir / "documents" / "doc1.txt").exists()
        assert (temp_dir / "documents" / "doc2.pdf").exists()
        assert (temp_dir / "images" / "image1.jpg").exists()
        assert (temp_dir / "images" / "image2.png").exists()
        assert (temp_dir / "videos" / "video.mp4").exists()
        assert (temp_dir / "other" / "unknown.xyz").exists()
        
        # Verify original files don't exist
        assert not (temp_dir / "doc1.txt").exists()
        assert not (temp_dir / "image1.jpg").exists()
    
    def test_organize_by_date_workflow(self, temp_dir):
        """Test complete organize workflow by date."""
        # Create files with different modification times
        import time
        from datetime import datetime, timedelta
        
        file1 = temp_dir / "recent.txt"
        file1.write_text("Recent file")
        
        file2 = temp_dir / "old.txt"
        file2.write_text("Old file")
        
        # Execute organize task
        coordinator = TaskCoordinator()
        options = {'rule_type': 'date', 'conflict_strategy': 'skip'}
        
        result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=False)
        
        # Verify results
        assert result.success_count == 2
        assert result.failure_count == 0
        
        # Verify files were organized into date folders
        # Files should be in YYYY-MM format folders
        date_folders = [d for d in temp_dir.iterdir() if d.is_dir()]
        assert len(date_folders) > 0
        
        # Verify original files don't exist in root
        assert not (temp_dir / "recent.txt").exists()
        assert not (temp_dir / "old.txt").exists()
    
    def test_organize_handles_conflicts(self, temp_dir):
        """Test organize workflow handles file conflicts correctly."""
        # Create files and pre-existing destination
        (temp_dir / "file.txt").write_text("Original")
        
        # Create destination directory with existing file
        dest_dir = temp_dir / "documents"
        dest_dir.mkdir()
        (dest_dir / "file.txt").write_text("Existing")
        
        # Execute organize with skip strategy
        coordinator = TaskCoordinator()
        options = {'rule_type': 'type', 'conflict_strategy': 'skip'}
        
        result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=False)
        
        # File should be skipped
        assert result.failure_count == 1
        
        # Existing file should be unchanged
        assert (dest_dir / "file.txt").read_text() == "Existing"


class TestEndToEndSummarizeWorkflow:
    """Test end-to-end summarize workflow."""
    
    def test_summarize_workflow_basic(self, temp_dir):
        """Test complete summarize workflow."""
        # Create test files with content
        (temp_dir / "file1.txt").write_text("Line 1\nLine 2\nLine 3")
        (temp_dir / "file2.txt").write_text("Word1 Word2 Word3\nWord4 Word5")
        
        # Execute summarize task
        coordinator = TaskCoordinator()
        options = {}
        
        result = coordinator.execute_task('summarize', str(temp_dir), options, dry_run=False)
        
        # Verify results
        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.operations) == 2
    
    def test_summarize_workflow_with_output_file(self, temp_dir):
        """Test summarize workflow with output file."""
        # Create test files
        (temp_dir / "file1.txt").write_text("Content line 1\nContent line 2")
        (temp_dir / "file2.txt").write_text("More content")
        
        # Execute summarize task with output file
        output_file = temp_dir / "summary.txt"
        coordinator = TaskCoordinator()
        options = {'output_file': str(output_file)}
        
        result = coordinator.execute_task('summarize', str(temp_dir), options, dry_run=False)
        
        # Verify results
        assert result.success_count == 2
        
        # Verify output file was created
        assert output_file.exists()
        
        # Verify output contains expected information
        summary_content = output_file.read_text()
        assert "FILE SUMMARY REPORT" in summary_content
        assert "file1.txt" in summary_content
        assert "file2.txt" in summary_content
        assert "Total Files: 2" in summary_content
    
    def test_summarize_detects_json_format(self, temp_dir):
        """Test summarize workflow detects JSON format."""
        # Create JSON file
        json_file = temp_dir / "data.json"
        json_file.write_text('{"key": "value", "number": 42}')
        
        # Execute summarize task
        coordinator = TaskCoordinator()
        options = {}
        
        result = coordinator.execute_task('summarize', str(temp_dir), options, dry_run=False)
        
        # Verify JSON was processed
        assert result.success_count == 1
    
    def test_summarize_detects_csv_format(self, temp_dir):
        """Test summarize workflow detects CSV format."""
        # Create CSV file
        csv_file = temp_dir / "data.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA")
        
        # Execute summarize task
        coordinator = TaskCoordinator()
        options = {}
        
        result = coordinator.execute_task('summarize', str(temp_dir), options, dry_run=False)
        
        # Verify CSV was processed
        assert result.success_count == 1


class TestPreviewThenExecuteWorkflow:
    """Test preview-then-execute workflow."""
    
    def test_preview_mode_does_not_modify_files(self, temp_dir):
        """Test that preview mode doesn't modify any files."""
        # Create test files
        original_files = []
        for i in range(3):
            file_path = temp_dir / f"file_{i}.txt"
            file_path.write_text(f"Content {i}")
            original_files.append((file_path, file_path.read_text()))
        
        # Execute rename in preview mode
        coordinator = TaskCoordinator()
        options = {'pattern': 'renamed_{n}.txt'}
        
        result = coordinator.execute_task('rename', str(temp_dir), options, dry_run=True)
        
        # Verify preview shows operations
        assert len(result.operations) == 3
        
        # Verify NO files were actually modified
        for file_path, original_content in original_files:
            assert file_path.exists()
            assert file_path.read_text() == original_content
        
        # Verify new files don't exist
        for i in range(1, 4):
            assert not (temp_dir / f"renamed_{i}.txt").exists()
    
    def test_preview_then_execute_rename(self, temp_dir):
        """Test preview followed by actual execution."""
        # Create test files
        for i in range(3):
            (temp_dir / f"old_{i}.txt").write_text(f"Content {i}")
        
        coordinator = TaskCoordinator()
        options = {'pattern': 'new_{n}.txt'}
        
        # First, preview
        preview_result = coordinator.execute_task('rename', str(temp_dir), options, dry_run=True)
        
        # Verify preview shows operations but doesn't execute
        assert len(preview_result.operations) == 3
        assert (temp_dir / "old_0.txt").exists()
        
        # Then, execute
        execute_result = coordinator.execute_task('rename', str(temp_dir), options, dry_run=False)
        
        # Verify execution completed
        assert execute_result.success_count == 3
        assert (temp_dir / "new_1.txt").exists()
        assert not (temp_dir / "old_0.txt").exists()
    
    def test_preview_then_execute_organize(self, temp_dir):
        """Test preview followed by actual execution for organize."""
        # Create test files
        (temp_dir / "doc.txt").write_text("Document")
        (temp_dir / "pic.jpg").write_text("Image")
        
        coordinator = TaskCoordinator()
        options = {'rule_type': 'type', 'conflict_strategy': 'skip'}
        
        # First, preview
        preview_result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=True)
        
        # Verify preview shows operations but doesn't execute
        assert len(preview_result.operations) == 2
        assert (temp_dir / "doc.txt").exists()
        assert not (temp_dir / "documents").exists()
        
        # Then, execute
        execute_result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=False)
        
        # Verify execution completed
        assert execute_result.success_count == 2
        assert (temp_dir / "documents" / "doc.txt").exists()
        assert not (temp_dir / "doc.txt").exists()
    
    def test_preview_mode_for_all_task_types(self, temp_dir):
        """Test that preview mode works for all task types."""
        # Create test files
        (temp_dir / "file.txt").write_text("Content")
        (temp_dir / "image.jpg").write_text("Image")
        
        coordinator = TaskCoordinator()
        
        # Test rename preview
        rename_result = coordinator.execute_task(
            'rename', str(temp_dir), 
            {'pattern': 'new_{n}.txt'}, 
            dry_run=True
        )
        assert len(rename_result.operations) > 0
        assert (temp_dir / "file.txt").exists()
        
        # Test organize preview
        organize_result = coordinator.execute_task(
            'organize', str(temp_dir),
            {'rule_type': 'type', 'conflict_strategy': 'skip'},
            dry_run=True
        )
        assert len(organize_result.operations) > 0
        assert (temp_dir / "file.txt").exists()
        
        # Test summarize preview
        summarize_result = coordinator.execute_task(
            'summarize', str(temp_dir),
            {},
            dry_run=True
        )
        assert len(summarize_result.operations) > 0


class TestCLIIntegration:
    """Test CLI integration with task execution."""
    
    def test_cli_rename_integration(self, temp_dir, monkeypatch):
        """Test CLI integration for rename task."""
        # Create test files
        for i in range(3):
            (temp_dir / f"file_{i}.txt").write_text(f"Content {i}")
        
        # Mock sys.argv
        test_args = [
            'lazy-auto',
            'rename',
            str(temp_dir),
            '--pattern', 'renamed_{n}.txt',
            '--no-confirm'
        ]
        
        # Parse arguments
        args = parse_arguments(test_args[1:])
        
        # Verify arguments parsed correctly
        assert args.task == 'rename'
        assert args.directory == str(temp_dir)
        assert args.pattern == 'renamed_{n}.txt'
        assert args.no_confirm is True
        
        # Execute task
        exit_code = execute_task(args)
        
        # Verify execution succeeded
        assert exit_code == 0
        assert (temp_dir / "renamed_1.txt").exists()
    
    def test_cli_organize_integration(self, temp_dir, monkeypatch):
        """Test CLI integration for organize task."""
        # Create test files
        (temp_dir / "doc.txt").write_text("Document")
        (temp_dir / "pic.jpg").write_text("Image")
        
        # Mock sys.argv
        test_args = [
            'lazy-auto',
            'organize',
            str(temp_dir),
            '--rule-type', 'type',
            '--no-confirm'
        ]
        
        # Parse arguments
        args = parse_arguments(test_args[1:])
        
        # Verify arguments parsed correctly
        assert args.task == 'organize'
        assert args.rule_type == 'type'
        
        # Execute task
        exit_code = execute_task(args)
        
        # Verify execution succeeded
        assert exit_code == 0
        assert (temp_dir / "documents" / "doc.txt").exists()
    
    def test_cli_dry_run_integration(self, temp_dir):
        """Test CLI dry-run mode integration."""
        # Create test files
        (temp_dir / "file.txt").write_text("Content")
        
        # Test with dry-run flag
        test_args = [
            'lazy-auto',
            'rename',
            str(temp_dir),
            '--pattern', 'new.txt',
            '--dry-run'
        ]
        
        args = parse_arguments(test_args[1:])
        assert args.dry_run is True
        
        # Execute task
        exit_code = execute_task(args)
        
        # Verify no changes were made
        assert exit_code == 0
        assert (temp_dir / "file.txt").exists()
        assert not (temp_dir / "new.txt").exists()


class TestErrorHandlingIntegration:
    """Test error handling in end-to-end workflows."""
    
    def test_partial_failure_continues_processing(self, temp_dir):
        """Test that partial failures don't stop processing."""
        # Create test files
        (temp_dir / "file1.txt").write_text("Content 1")
        (temp_dir / "file2.txt").write_text("Content 2")
        (temp_dir / "file3.txt").write_text("Content 3")
        
        # Create a subdirectory that will cause one file to fail
        subdir = temp_dir / "documents"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("Existing")
        
        # Execute organize with skip strategy
        coordinator = TaskCoordinator()
        options = {'rule_type': 'type', 'conflict_strategy': 'skip'}
        
        result = coordinator.execute_task('organize', str(temp_dir), options, dry_run=False)
        
        # Verify some succeeded and some failed
        assert result.success_count == 2  # file1 and file3
        assert result.failure_count == 1  # file2 (conflict)
        assert len(result.errors) == 1
    
    def test_invalid_directory_error(self):
        """Test error handling for invalid directory."""
        coordinator = TaskCoordinator()
        options = {'pattern': 'new_{n}.txt'}
        
        # Try to execute on non-existent directory
        with pytest.raises(FileNotFoundError):
            coordinator.execute_task('rename', '/nonexistent/path', options, dry_run=False)
    
    def test_invalid_task_type_error(self, temp_dir):
        """Test error handling for invalid task type."""
        coordinator = TaskCoordinator()
        
        # Try to execute invalid task type
        with pytest.raises(ValueError, match="Unknown task type"):
            coordinator.execute_task('invalid_task', str(temp_dir), {}, dry_run=False)
