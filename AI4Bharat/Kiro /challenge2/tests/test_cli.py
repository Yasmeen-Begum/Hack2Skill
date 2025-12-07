"""Tests for CLI interface and argument parsing."""

import pytest
import sys
from io import StringIO
from pathlib import Path
from lazy_automation.cli.main import (
    parse_arguments,
    validate_arguments,
    build_task_options,
    get_task_module,
    confirm_execution,
    execute_task
)
from lazy_automation.tasks.rename import RenameTask
from lazy_automation.tasks.organize import OrganizeTask
from lazy_automation.tasks.summarize import SummarizeTask
from lazy_automation.reporting import Reporter


class TestArgumentParsing:
    """Unit tests for argument parsing."""
    
    def test_parse_rename_with_required_args(self):
        """Test parsing rename task with required arguments."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'file_{n}.txt'])
        
        assert args.task == 'rename'
        assert args.directory == '/test/dir'
        assert args.pattern == 'file_{n}.txt'
        assert args.dry_run is False
        assert args.verbose is False
    
    def test_parse_organize_with_required_args(self):
        """Test parsing organize task with required arguments."""
        args = parse_arguments(['organize', '/test/dir', '--rule-type', 'type'])
        
        assert args.task == 'organize'
        assert args.directory == '/test/dir'
        assert args.rule_type == 'type'
        assert args.conflict_strategy == 'skip'
    
    def test_parse_summarize_with_required_args(self):
        """Test parsing summarize task with required arguments."""
        args = parse_arguments(['summarize', '/test/dir'])
        
        assert args.task == 'summarize'
        assert args.directory == '/test/dir'
        assert args.output is None
    
    def test_parse_with_dry_run_flag(self):
        """Test parsing with dry-run flag."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'test', '--dry-run'])
        
        assert args.dry_run is True
    
    def test_parse_with_verbose_flag(self):
        """Test parsing with verbose flag."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'test', '--verbose'])
        
        assert args.verbose is True
    
    def test_parse_with_extensions_filter(self):
        """Test parsing with extension filters."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'test', '--extensions', '.txt', '.pdf'])
        
        assert args.extensions == ['.txt', '.pdf']
    
    def test_parse_with_no_confirm_flag(self):
        """Test parsing with no-confirm flag."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'test', '--no-confirm'])
        
        assert args.no_confirm is True
    
    def test_parse_organize_with_conflict_strategy(self):
        """Test parsing organize with conflict strategy."""
        args = parse_arguments(['organize', '/test/dir', '--rule-type', 'date', '--conflict-strategy', 'overwrite'])
        
        assert args.conflict_strategy == 'overwrite'
    
    def test_parse_summarize_with_output_file(self):
        """Test parsing summarize with output file."""
        args = parse_arguments(['summarize', '/test/dir', '--output', 'summary.txt'])
        
        assert args.output == 'summary.txt'
    
    def test_parse_invalid_task_type(self):
        """Test parsing with invalid task type."""
        with pytest.raises(SystemExit):
            parse_arguments(['invalid', '/test/dir'])
    
    def test_parse_missing_required_directory(self):
        """Test parsing without required directory argument."""
        with pytest.raises(SystemExit):
            parse_arguments(['rename'])
    
    def test_parse_invalid_rule_type(self):
        """Test parsing organize with invalid rule type."""
        with pytest.raises(SystemExit):
            parse_arguments(['organize', '/test/dir', '--rule-type', 'invalid'])
    
    def test_parse_invalid_conflict_strategy(self):
        """Test parsing organize with invalid conflict strategy."""
        with pytest.raises(SystemExit):
            parse_arguments(['organize', '/test/dir', '--rule-type', 'type', '--conflict-strategy', 'invalid'])


class TestArgumentValidation:
    """Unit tests for argument validation."""
    
    def test_validate_nonexistent_directory(self, tmp_path):
        """Test validation fails for nonexistent directory."""
        args = parse_arguments(['rename', str(tmp_path / 'nonexistent'), '--pattern', 'test'])
        
        with pytest.raises(ValueError, match="Directory does not exist"):
            validate_arguments(args)
    
    def test_validate_file_instead_of_directory(self, tmp_path):
        """Test validation fails when path is a file, not directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        args = parse_arguments(['rename', str(test_file), '--pattern', 'test'])
        
        with pytest.raises(ValueError, match="Path is not a directory"):
            validate_arguments(args)
    
    def test_validate_rename_missing_pattern(self, tmp_path):
        """Test validation fails for rename without pattern."""
        args = parse_arguments(['rename', str(tmp_path)])
        
        with pytest.raises(ValueError, match="--pattern is required"):
            validate_arguments(args)
    
    def test_validate_organize_missing_rule_type(self, tmp_path):
        """Test validation fails for organize without rule-type."""
        args = parse_arguments(['organize', str(tmp_path)])
        
        with pytest.raises(ValueError, match="--rule-type is required"):
            validate_arguments(args)
    
    def test_validate_valid_rename_args(self, tmp_path):
        """Test validation passes for valid rename arguments."""
        args = parse_arguments(['rename', str(tmp_path), '--pattern', 'file_{n}.txt'])
        
        # Should not raise
        validate_arguments(args)
    
    def test_validate_valid_organize_args(self, tmp_path):
        """Test validation passes for valid organize arguments."""
        args = parse_arguments(['organize', str(tmp_path), '--rule-type', 'type'])
        
        # Should not raise
        validate_arguments(args)
    
    def test_validate_valid_summarize_args(self, tmp_path):
        """Test validation passes for valid summarize arguments."""
        args = parse_arguments(['summarize', str(tmp_path)])
        
        # Should not raise
        validate_arguments(args)


class TestTaskOptions:
    """Unit tests for building task options."""
    
    def test_build_rename_options(self):
        """Test building options for rename task."""
        args = parse_arguments(['rename', '/test/dir', '--pattern', 'file_{n}.txt', '--extensions', '.txt', '.pdf'])
        options = build_task_options(args)
        
        assert options['pattern'] == 'file_{n}.txt'
        assert options['extensions'] == ['.txt', '.pdf']
    
    def test_build_organize_options(self):
        """Test building options for organize task."""
        args = parse_arguments(['organize', '/test/dir', '--rule-type', 'date', '--conflict-strategy', 'rename'])
        options = build_task_options(args)
        
        assert options['rule_type'] == 'date'
        assert options['conflict_strategy'] == 'rename'
    
    def test_build_summarize_options_with_output(self):
        """Test building options for summarize task with output file."""
        args = parse_arguments(['summarize', '/test/dir', '--output', 'summary.txt'])
        options = build_task_options(args)
        
        assert options['output_file'] == 'summary.txt'
    
    def test_build_summarize_options_without_output(self):
        """Test building options for summarize task without output file."""
        args = parse_arguments(['summarize', '/test/dir'])
        options = build_task_options(args)
        
        assert 'output_file' not in options
    
    def test_build_options_with_extensions(self):
        """Test building options with extension filters."""
        args = parse_arguments(['summarize', '/test/dir', '--extensions', '.txt', '.md'])
        options = build_task_options(args)
        
        assert options['extensions'] == ['.txt', '.md']


class TestTaskModuleSelection:
    """Unit tests for task module selection."""
    
    def test_get_rename_task_module(self):
        """Test getting rename task module."""
        module = get_task_module('rename')
        assert isinstance(module, RenameTask)
    
    def test_get_organize_task_module(self):
        """Test getting organize task module."""
        module = get_task_module('organize')
        assert isinstance(module, OrganizeTask)
    
    def test_get_summarize_task_module(self):
        """Test getting summarize task module."""
        module = get_task_module('summarize')
        assert isinstance(module, SummarizeTask)
    
    def test_get_invalid_task_module(self):
        """Test getting invalid task module raises error."""
        with pytest.raises(ValueError, match="Unknown task type"):
            get_task_module('invalid')


class TestConfirmation:
    """Unit tests for confirmation prompts."""
    
    def test_confirm_execution_yes(self, monkeypatch):
        """Test confirmation with 'yes' response."""
        monkeypatch.setattr('builtins.input', lambda: 'yes')
        
        output = StringIO()
        reporter = Reporter(output=output)
        
        result = confirm_execution(reporter)
        assert result is True
    
    def test_confirm_execution_y(self, monkeypatch):
        """Test confirmation with 'y' response."""
        monkeypatch.setattr('builtins.input', lambda: 'y')
        
        output = StringIO()
        reporter = Reporter(output=output)
        
        result = confirm_execution(reporter)
        assert result is True
    
    def test_confirm_execution_no(self, monkeypatch):
        """Test confirmation with 'no' response."""
        monkeypatch.setattr('builtins.input', lambda: 'no')
        
        output = StringIO()
        reporter = Reporter(output=output)
        
        result = confirm_execution(reporter)
        assert result is False
    
    def test_confirm_execution_n(self, monkeypatch):
        """Test confirmation with 'n' response."""
        monkeypatch.setattr('builtins.input', lambda: 'n')
        
        output = StringIO()
        reporter = Reporter(output=output)
        
        result = confirm_execution(reporter)
        assert result is False
    
    def test_confirm_execution_keyboard_interrupt(self, monkeypatch):
        """Test confirmation handles keyboard interrupt."""
        def raise_interrupt():
            raise KeyboardInterrupt()
        
        monkeypatch.setattr('builtins.input', lambda: raise_interrupt())
        
        output = StringIO()
        reporter = Reporter(output=output)
        
        result = confirm_execution(reporter)
        assert result is False


class TestExecuteTask:
    """Unit tests for task execution."""
    
    def test_execute_rename_dry_run(self, tmp_path):
        """Test executing rename task in dry-run mode."""
        # Create test files
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")
        
        args = parse_arguments([
            'rename', str(tmp_path),
            '--pattern', 'renamed_{n}.txt',
            '--dry-run'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 0
        # Files should not be renamed in dry-run
        assert (tmp_path / "file1.txt").exists()
        assert (tmp_path / "file2.txt").exists()
    
    def test_execute_organize_dry_run(self, tmp_path):
        """Test executing organize task in dry-run mode."""
        # Create test files
        (tmp_path / "test.txt").write_text("test")
        (tmp_path / "image.jpg").write_text("test")
        
        args = parse_arguments([
            'organize', str(tmp_path),
            '--rule-type', 'type',
            '--dry-run'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 0
        # Files should not be moved in dry-run
        assert (tmp_path / "test.txt").exists()
        assert (tmp_path / "image.jpg").exists()
    
    def test_execute_summarize_dry_run(self, tmp_path):
        """Test executing summarize task in dry-run mode."""
        # Create test file
        (tmp_path / "test.txt").write_text("Hello world\nTest content")
        
        args = parse_arguments([
            'summarize', str(tmp_path),
            '--dry-run'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 0
    
    def test_execute_with_no_files(self, tmp_path):
        """Test executing task with no matching files."""
        args = parse_arguments([
            'rename', str(tmp_path),
            '--pattern', 'test_{n}.txt',
            '--extensions', '.txt'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 0
    
    def test_execute_with_invalid_directory(self):
        """Test executing task with invalid directory."""
        args = parse_arguments([
            'rename', '/nonexistent/directory',
            '--pattern', 'test_{n}.txt'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 2  # Validation error
    
    def test_execute_rename_with_no_confirm(self, tmp_path):
        """Test executing rename with --no-confirm flag."""
        # Create test files
        (tmp_path / "file1.txt").write_text("test")
        
        args = parse_arguments([
            'rename', str(tmp_path),
            '--pattern', 'renamed_{n}.txt',
            '--no-confirm'
        ])
        
        exit_code = execute_task(args)
        
        assert exit_code == 0
        # File should be renamed
        assert (tmp_path / "renamed_1.txt").exists()
        assert not (tmp_path / "file1.txt").exists()


class TestHelpDisplay:
    """Unit tests for help display."""
    
    def test_help_flag_exits(self):
        """Test that --help flag causes system exit."""
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments(['--help'])
        
        assert exc_info.value.code == 0
    
    def test_help_displays_usage(self, capsys):
        """Test that help displays usage information."""
        with pytest.raises(SystemExit):
            parse_arguments(['--help'])
        
        captured = capsys.readouterr()
        assert 'lazy-auto' in captured.out
        assert 'rename' in captured.out
        assert 'organize' in captured.out
        assert 'summarize' in captured.out


class TestErrorMessages:
    """Unit tests for error messages."""
    
    def test_error_message_for_missing_pattern(self, tmp_path):
        """Test error message when pattern is missing for rename."""
        args = parse_arguments(['rename', str(tmp_path)])
        
        with pytest.raises(ValueError) as exc_info:
            validate_arguments(args)
        
        assert "--pattern is required" in str(exc_info.value)
    
    def test_error_message_for_missing_rule_type(self, tmp_path):
        """Test error message when rule-type is missing for organize."""
        args = parse_arguments(['organize', str(tmp_path)])
        
        with pytest.raises(ValueError) as exc_info:
            validate_arguments(args)
        
        assert "--rule-type is required" in str(exc_info.value)
    
    def test_error_message_for_nonexistent_directory(self):
        """Test error message for nonexistent directory."""
        args = parse_arguments(['rename', '/nonexistent', '--pattern', 'test'])
        
        with pytest.raises(ValueError) as exc_info:
            validate_arguments(args)
        
        assert "Directory does not exist" in str(exc_info.value)
    
    def test_error_message_for_invalid_task_module(self):
        """Test error message for invalid task type."""
        with pytest.raises(ValueError) as exc_info:
            get_task_module('invalid_task')
        
        assert "Unknown task type" in str(exc_info.value)
