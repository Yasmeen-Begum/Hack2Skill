"""Tests for rename task module."""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from lazy_automation.tasks.rename import RenameTask
from lazy_automation.tasks.base import Operation


class TestRenameTask:
    """Unit and property tests for rename task."""
    
    @given(
        num_files=st.integers(min_value=1, max_value=20),
        pattern=st.sampled_from([
            "file_{n}.txt",
            "doc_{n}.md",
            "image_{n}.jpg",
            "{name}_{n}.txt",
            "renamed_{n}{ext}"
        ])
    )
    @settings(max_examples=100)
    def test_rename_pattern_application(self, num_files, pattern):
        """
        **Feature: lazy-automation-tool, Property 1: Rename pattern application**
        **Validates: Requirements 1.1, 1.2**
        
        For any directory with files and any valid renaming pattern, applying the pattern
        should result in all matching files having names that conform to the pattern rules,
        including sequential numbering when specified.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            files = []
            for i in range(num_files):
                file_path = Path(tmpdir) / f"test_{i}.txt"
                file_path.touch()
                files.append(str(file_path))
            
            # Create rename task and plan operations
            task = RenameTask()
            operations = task.plan(tmpdir, {'pattern': pattern})
            
            # Verify we have operations for all files
            assert len(operations) == num_files
            
            # Verify all operations are rename type
            assert all(op.type == "rename" for op in operations)
            
            # Verify sequential numbering if pattern contains {n}
            if '{n}' in pattern:
                for idx, op in enumerate(operations, start=1):
                    dest_name = Path(op.destination).name
                    assert str(idx) in dest_name, f"Sequential number {idx} not found in {dest_name}"
            
            # Verify all destinations are unique (no duplicates)
            destinations = [op.destination for op in operations]
            assert len(destinations) == len(set(destinations)), "Duplicate destinations found"
            
            # Verify pattern metadata is stored
            assert all(op.metadata.get('pattern') == pattern for op in operations)
            assert all(op.metadata.get('index') == idx for idx, op in enumerate(operations, start=1))

    @given(
        num_files=st.integers(min_value=2, max_value=15),
        duplicate_pattern=st.sampled_from([
            "same_name.txt",  # All files get same name
            "file.txt",
            "duplicate.md"
        ])
    )
    @settings(max_examples=100)
    def test_duplicate_detection_prevents_conflicts(self, num_files, duplicate_pattern):
        """
        **Feature: lazy-automation-tool, Property 2: Duplicate detection prevents conflicts**
        **Validates: Requirements 1.3**
        
        For any set of rename operations that would create duplicate filenames,
        the conflict detection should identify all duplicates and prevent execution.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files with different names
            for i in range(num_files):
                file_path = Path(tmpdir) / f"unique_{i}.txt"
                file_path.touch()
            
            # Create rename task
            task = RenameTask()
            
            # Try to plan operations with a pattern that creates duplicates
            with pytest.raises(ValueError) as exc_info:
                task.plan(tmpdir, {'pattern': duplicate_pattern})
            
            # Verify the error message mentions duplicates/conflicts
            error_msg = str(exc_info.value).lower()
            assert 'duplicate' in error_msg or 'conflict' in error_msg
