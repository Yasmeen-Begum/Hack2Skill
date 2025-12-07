"""Unit tests for task coordinator error handling."""

import pytest
from pathlib import Path
from lazy_automation.coordinator import TaskCoordinator
from lazy_automation.reporting import Reporter
from io import StringIO


class TestCoordinatorErrorHandling:
    """Test error handling in the task coordinator."""
    
    def test_invalid_task_type(self, temp_dir):
        """Test that invalid task types raise ValueError with helpful message."""
        coordinator = TaskCoordinator()
        
        with pytest.raises(ValueError) as exc_info:
            coordinator.execute_task(
                task_type='invalid_task',
                directory=str(temp_dir),
                options={},
                dry_run=True
            )
        
        # Check error message includes available tasks
        error_msg = str(exc_info.value)
        assert 'invalid_task' in error_msg
        assert 'rename' in error_msg
        assert 'organize' in error_msg
        assert 'summarize' in error_msg
    
    def test_permission_error_reporting(self, temp_dir, monkeypatch):
        """Test that permission errors are caught and reported properly."""
        # Create a file
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        # Mock the rename operation to raise PermissionError
        from lazy_automation.tasks import rename
        original_rename = rename.rename_file
        
        def mock_rename(*args, **kwargs):
            raise PermissionError("Permission denied: test.txt")
        
        monkeypatch.setattr(rename, 'rename_file', mock_rename)
        
        # Create coordinator with string output for testing
        output = StringIO()
        reporter = Reporter(verbose=True, output=output)
        coordinator = TaskCoordinator(reporter=reporter)
        
        # Execute task - errors are caught by the task module and returned in result
        result = coordinator.execute_task(
            task_type='rename',
            directory=str(temp_dir),
            options={'pattern': 'new_{n}.txt'},
            dry_run=False
        )
        
        # Check that the operation failed
        assert result.failure_count == 1
        assert result.success_count == 0
        assert len(result.errors) == 1
        
        # Check error details
        error = result.errors[0]
        assert 'Permission denied' in error['error']
    
    def test_file_not_found_error_reporting(self):
        """Test that FileNotFoundError is caught and reported properly."""
        output = StringIO()
        reporter = Reporter(verbose=True, output=output)
        coordinator = TaskCoordinator(reporter=reporter)
        
        # Try to execute task on non-existent directory
        with pytest.raises(FileNotFoundError) as exc_info:
            coordinator.execute_task(
                task_type='rename',
                directory='/nonexistent/directory',
                options={'pattern': 'new_{n}.txt'},
                dry_run=False
            )
        
        # Check error message
        assert 'not found' in str(exc_info.value).lower()
        
        # Check that error was logged
        log_entries = reporter.get_log_entries()
        assert any('[ERROR]' in entry for entry in log_entries)
    
    def test_partial_failure_scenario(self, temp_dir, monkeypatch):
        """Test that partial failures are handled correctly."""
        # Create multiple files
        for i in range(5):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")
        
        # Mock rename to fail on specific files
        from lazy_automation.tasks import rename
        original_rename = rename.rename_file
        call_count = [0]
        
        def mock_rename(old_path, new_path, dry_run=False):
            call_count[0] += 1
            # Fail on the 3rd file
            if call_count[0] == 3:
                raise PermissionError(f"Permission denied: {old_path}")
            return original_rename(old_path, new_path, dry_run)
        
        monkeypatch.setattr(rename, 'rename_file', mock_rename)
        
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        coordinator = TaskCoordinator(reporter=reporter)
        
        # Execute task
        result = coordinator.execute_task(
            task_type='rename',
            directory=str(temp_dir),
            options={'pattern': 'renamed_{n}.txt'},
            dry_run=False
        )
        
        # Check that some succeeded and some failed
        assert result.success_count == 4  # 4 out of 5 should succeed
        assert result.failure_count == 1  # 1 should fail
        assert len(result.errors) == 1
        
        # Check error details
        error = result.errors[0]
        assert 'Permission denied' in error['error']
    
    def test_error_message_formatting(self, temp_dir):
        """Test that error messages are properly formatted and informative."""
        output = StringIO()
        reporter = Reporter(verbose=True, output=output)
        coordinator = TaskCoordinator(reporter=reporter)
        
        # Test with missing required option
        with pytest.raises(ValueError) as exc_info:
            coordinator.execute_task(
                task_type='rename',
                directory=str(temp_dir),
                options={},  # Missing 'pattern'
                dry_run=True
            )
        
        # Check error message is informative
        error_msg = str(exc_info.value)
        assert 'pattern' in error_msg.lower() or 'required' in error_msg.lower()
        
        # Check that error was logged with proper level
        log_entries = reporter.get_log_entries()
        assert any('[ERROR]' in entry for entry in log_entries)
    
    def test_get_task_module_invalid_type(self):
        """Test get_task_module with invalid task type."""
        coordinator = TaskCoordinator()
        
        with pytest.raises(ValueError) as exc_info:
            coordinator.get_task_module('nonexistent')
        
        error_msg = str(exc_info.value)
        assert 'nonexistent' in error_msg
        assert 'rename' in error_msg
        assert 'organize' in error_msg
        assert 'summarize' in error_msg
    
    def test_get_task_module_valid_types(self):
        """Test get_task_module returns correct module instances."""
        coordinator = TaskCoordinator()
        
        from lazy_automation.tasks.rename import RenameTask
        from lazy_automation.tasks.organize import OrganizeTask
        from lazy_automation.tasks.summarize import SummarizeTask
        
        rename_module = coordinator.get_task_module('rename')
        assert isinstance(rename_module, RenameTask)
        
        organize_module = coordinator.get_task_module('organize')
        assert isinstance(organize_module, OrganizeTask)
        
        summarize_module = coordinator.get_task_module('summarize')
        assert isinstance(summarize_module, SummarizeTask)
    
    def test_coordinator_with_default_reporter(self, temp_dir):
        """Test that coordinator works with default reporter."""
        # Create a file
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        # Create coordinator without explicit reporter
        coordinator = TaskCoordinator()
        
        # Execute task in dry-run mode
        result = coordinator.execute_task(
            task_type='rename',
            directory=str(temp_dir),
            options={'pattern': 'new_{n}.txt'},
            dry_run=True
        )
        
        # Should succeed
        assert result.success_count == 1
        assert result.failure_count == 0
    
    def test_error_aggregation_multiple_failures(self, temp_dir, monkeypatch):
        """Test that multiple errors are properly aggregated."""
        # Create multiple files
        for i in range(5):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")
        
        # Mock rename to fail on multiple files
        from lazy_automation.tasks import rename
        original_rename = rename.rename_file
        call_count = [0]
        
        def mock_rename(old_path, new_path, dry_run=False):
            call_count[0] += 1
            # Fail on files 2 and 4
            if call_count[0] in [2, 4]:
                raise PermissionError(f"Permission denied: {old_path}")
            return original_rename(old_path, new_path, dry_run)
        
        monkeypatch.setattr(rename, 'rename_file', mock_rename)
        
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        coordinator = TaskCoordinator(reporter=reporter)
        
        # Execute task
        result = coordinator.execute_task(
            task_type='rename',
            directory=str(temp_dir),
            options={'pattern': 'renamed_{n}.txt'},
            dry_run=False
        )
        
        # Check that errors are aggregated
        assert result.success_count == 3
        assert result.failure_count == 2
        assert len(result.errors) == 2
        
        # All errors should be reported
        for error in result.errors:
            assert 'Permission denied' in error['error']
