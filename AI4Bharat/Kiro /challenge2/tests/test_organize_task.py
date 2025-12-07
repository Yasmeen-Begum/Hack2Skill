"""Tests for organize task module."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from lazy_automation.tasks.organize import OrganizeTask
from lazy_automation.tasks.base import Operation


class TestOrganizeTask:
    """Unit and property tests for organize task."""
    
    @given(
        num_files=st.integers(min_value=1, max_value=20),
        rule_type=st.sampled_from(['type', 'date'])
    )
    @settings(max_examples=100)
    def test_organization_by_rules(self, num_files, rule_type):
        """
        **Feature: lazy-automation-tool, Property 5: Organization by rules**
        **Validates: Requirements 2.1, 2.2**
        
        For any set of files and organization rules (type-based or age-based),
        all files should be moved to subdirectories that match their characteristics
        according to the rules.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files with various extensions and dates
            extensions = ['.jpg', '.txt', '.pdf', '.mp3', '.py', '.zip', '.doc']
            files_created = []
            
            for i in range(num_files):
                ext = extensions[i % len(extensions)]
                file_path = Path(tmpdir) / f"test_{i}{ext}"
                file_path.touch()
                
                # Set different modification times for date-based testing
                if rule_type == 'date':
                    # Set file modification time to various dates in the past
                    days_ago = i * 10  # Spread files across different dates
                    mtime = datetime.now() - timedelta(days=days_ago)
                    timestamp = mtime.timestamp()
                    os.utime(str(file_path), (timestamp, timestamp))
                
                files_created.append(str(file_path))
            
            # Create organize task and plan operations
            task = OrganizeTask()
            operations = task.plan(tmpdir, {'rule_type': rule_type})
            
            # Verify we have operations for all files
            assert len(operations) == num_files
            
            # Verify all operations are move type
            assert all(op.type == "move" for op in operations)
            
            # Verify files are organized according to rules
            if rule_type == 'type':
                # Check that files are grouped by their type category
                for op in operations:
                    source_file = Path(op.source)
                    dest_file = Path(op.destination)
                    
                    # Destination should be in a subdirectory
                    assert dest_file.parent != source_file.parent
                    
                    # Category should match file extension
                    category = op.metadata.get('category')
                    assert category is not None
                    
                    # Verify the category is in the destination path
                    assert category in str(dest_file.parent)
                    
                    # Verify file is classified correctly
                    ext = source_file.suffix.lower()
                    expected_category = task._classify_file_type(source_file)
                    assert category == expected_category
            
            elif rule_type == 'date':
                # Check that files are grouped by date
                for op in operations:
                    source_file = Path(op.source)
                    dest_file = Path(op.destination)
                    
                    # Destination should be in a subdirectory
                    assert dest_file.parent != source_file.parent
                    
                    # Date folder should be in metadata
                    date_folder = op.metadata.get('date_folder')
                    assert date_folder is not None
                    
                    # Verify the date folder is in the destination path
                    assert date_folder in str(dest_file.parent)
            
            # Verify metadata is stored correctly
            assert all(op.metadata.get('rule_type') == rule_type for op in operations)
    
    @given(
        num_files=st.integers(min_value=1, max_value=15),
        rule_type=st.sampled_from(['type', 'date'])
    )
    @settings(max_examples=100)
    def test_directory_creation_completeness(self, num_files, rule_type):
        """
        **Feature: lazy-automation-tool, Property 6: Directory creation completeness**
        **Validates: Requirements 2.3**
        
        For any organization operation requiring non-existent directories,
        all necessary directories should be created before file moves.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            extensions = ['.jpg', '.txt', '.pdf', '.mp3', '.py']
            for i in range(num_files):
                ext = extensions[i % len(extensions)]
                file_path = Path(tmpdir) / f"file_{i}{ext}"
                file_path.touch()
                
                # Set different modification times for date-based testing
                if rule_type == 'date':
                    days_ago = i * 15
                    mtime = datetime.now() - timedelta(days=days_ago)
                    timestamp = mtime.timestamp()
                    os.utime(str(file_path), (timestamp, timestamp))
            
            # Plan operations
            task = OrganizeTask()
            operations = task.plan(tmpdir, {'rule_type': rule_type})
            
            # Collect all unique destination directories
            dest_dirs = set()
            for op in operations:
                dest_dir = Path(op.destination).parent
                dest_dirs.add(dest_dir)
            
            # Verify that destination directories don't exist yet
            for dest_dir in dest_dirs:
                assert not dest_dir.exists(), f"Directory {dest_dir} should not exist before execution"
            
            # Execute operations (not in dry-run mode)
            result = task.execute(operations, dry_run=False)
            
            # Verify all destination directories were created
            for dest_dir in dest_dirs:
                assert dest_dir.exists(), f"Directory {dest_dir} should exist after execution"
                assert dest_dir.is_dir(), f"{dest_dir} should be a directory"
            
            # Verify all files were moved successfully
            assert result.success_count == num_files
            assert result.failure_count == 0
            
            # Verify files are in their new locations
            for op in operations:
                dest_path = Path(op.destination)
                assert dest_path.exists(), f"File should exist at {dest_path}"
                assert dest_path.is_file(), f"{dest_path} should be a file"
    
    @given(
        num_files=st.integers(min_value=2, max_value=10),
        conflict_strategy=st.sampled_from(['skip', 'overwrite', 'rename'])
    )
    @settings(max_examples=100)
    def test_conflict_strategy_adherence(self, num_files, conflict_strategy):
        """
        **Feature: lazy-automation-tool, Property 7: Conflict strategy adherence**
        **Validates: Requirements 2.4**
        
        For any file move operation where the destination exists, the system should
        handle the conflict according to the specified strategy (skip, overwrite, or rename).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files that will all go to the same category
            # Use .txt extension so they all go to 'documents' category
            source_files = []
            for i in range(num_files):
                file_path = Path(tmpdir) / f"file_{i}.txt"
                file_path.write_text(f"Content {i}")
                source_files.append(file_path)
            
            # Plan operations
            task = OrganizeTask()
            operations = task.plan(tmpdir, {
                'rule_type': 'type',
                'conflict_strategy': conflict_strategy
            })
            
            # Pre-create the destination directory and one conflicting file
            dest_dir = Path(tmpdir) / 'documents'
            dest_dir.mkdir(exist_ok=True)
            
            # Create a conflict: pre-create the first destination file
            first_op = operations[0]
            conflict_file = Path(first_op.destination)
            original_content = "Original content"
            conflict_file.write_text(original_content)
            
            # Execute operations
            result = task.execute(operations, dry_run=False)
            
            # Verify conflict strategy was followed
            if conflict_strategy == 'skip':
                # First file should be skipped, rest should succeed
                assert result.failure_count >= 1, "At least one file should be skipped"
                
                # The conflicting file should still have original content
                if conflict_file.exists():
                    content = conflict_file.read_text()
                    assert content == original_content, "Skipped file should preserve original content"
            
            elif conflict_strategy == 'overwrite':
                # All files should succeed
                assert result.success_count == num_files, "All files should be moved with overwrite"
                
                # The conflicting file should have new content
                if conflict_file.exists():
                    content = conflict_file.read_text()
                    assert content != original_content, "Overwritten file should have new content"
            
            elif conflict_strategy == 'rename':
                # All files should succeed (conflict resolved by renaming)
                assert result.success_count == num_files, "All files should be moved with rename"
                
                # The original conflict file should still exist
                assert conflict_file.exists(), "Original file should still exist"
                
                # There should be a renamed version (e.g., file_0_1.txt)
                renamed_files = list(dest_dir.glob("file_0*.txt"))
                assert len(renamed_files) >= 2, "Should have original and renamed file"
            
            # Verify total operations attempted
            assert result.success_count + result.failure_count == num_files
