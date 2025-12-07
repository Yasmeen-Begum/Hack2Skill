"""Tests for file system operations."""

import pytest
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from lazy_automation.file_operations import (
    list_files, rename_file, move_file, get_file_metadata
)


class TestFileOperations:
    """Unit and property tests for file operations."""
    
    def test_list_files_basic(self):
        """Test basic file listing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.py").touch()
            (Path(tmpdir) / "file3.txt").touch()
            
            files = list_files(tmpdir)
            assert len(files) == 3
    
    def test_list_files_with_filter(self):
        """Test file listing with extension filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.py").touch()
            (Path(tmpdir) / "file3.txt").touch()
            
            files = list_files(tmpdir, extensions=['.txt'])
            assert len(files) == 2
            assert all(f.endswith('.txt') for f in files)
    
    def test_rename_file_basic(self):
        """Test basic file renaming."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = Path(tmpdir) / "old.txt"
            new_path = Path(tmpdir) / "new.txt"
            old_path.write_text("test content")
            
            rename_file(str(old_path), str(new_path), dry_run=False)
            
            assert not old_path.exists()
            assert new_path.exists()
            assert new_path.read_text() == "test content"
    
    def test_move_file_basic(self):
        """Test basic file moving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.txt"
            dst = Path(tmpdir) / "subdir" / "dest.txt"
            src.write_text("test content")
            
            success, actual_path = move_file(str(src), str(dst), dry_run=False)
            
            assert success
            assert not src.exists()
            assert Path(actual_path).exists()
            assert Path(actual_path).read_text() == "test content"


class TestPropertyBasedFileOperations:
    """Property-based tests for file operations."""
    
    @given(
        file_count=st.integers(min_value=1, max_value=20),
        extensions=st.lists(
            st.sampled_from(['.txt', '.py', '.json', '.csv', '.xml']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_property_preview_mode_preserves_filesystem_rename(self, file_count, extensions):
        """
        **Feature: lazy-automation-tool, Property 3: Preview mode preserves file system**
        
        For any automation operation executed in preview/dry-run mode,
        the file system should remain completely unchanged after execution.
        
        **Validates: Requirements 1.4, 4.2, 4.5**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create random files
            created_files = []
            for i in range(file_count):
                ext = extensions[i % len(extensions)]
                filepath = tmppath / f"file_{i}{ext}"
                filepath.write_text(f"content_{i}")
                created_files.append(filepath)
            
            # Capture initial state
            initial_files = set(p.name for p in tmppath.iterdir())
            initial_contents = {p.name: p.read_text() for p in tmppath.iterdir()}
            
            # Perform dry-run rename operations
            for i, filepath in enumerate(created_files):
                new_path = tmppath / f"renamed_{i}{filepath.suffix}"
                try:
                    rename_file(str(filepath), str(new_path), dry_run=True)
                except (FileNotFoundError, FileExistsError):
                    # Expected errors should not modify filesystem
                    pass
            
            # Verify filesystem unchanged
            final_files = set(p.name for p in tmppath.iterdir())
            final_contents = {p.name: p.read_text() for p in tmppath.iterdir()}
            
            assert initial_files == final_files, "File names changed during dry-run"
            assert initial_contents == final_contents, "File contents changed during dry-run"
    
    @given(
        file_count=st.integers(min_value=1, max_value=20),
        conflict_strategy=st.sampled_from(['skip', 'overwrite', 'rename'])
    )
    @settings(max_examples=100)
    def test_property_preview_mode_preserves_filesystem_move(self, file_count, conflict_strategy):
        """
        **Feature: lazy-automation-tool, Property 3: Preview mode preserves file system**
        
        For any move operation executed in preview/dry-run mode,
        the file system should remain completely unchanged after execution.
        
        **Validates: Requirements 1.4, 4.2, 4.5**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "subdir"
            
            # Create random files
            created_files = []
            for i in range(file_count):
                filepath = tmppath / f"file_{i}.txt"
                filepath.write_text(f"content_{i}")
                created_files.append(filepath)
            
            # Capture initial state (recursively)
            def get_all_files(path):
                files = {}
                for p in path.rglob('*'):
                    if p.is_file():
                        rel_path = p.relative_to(path)
                        files[str(rel_path)] = p.read_text()
                return files
            
            initial_state = get_all_files(tmppath)
            
            # Perform dry-run move operations
            for i, filepath in enumerate(created_files):
                dest = subdir / f"moved_{i}.txt"
                try:
                    move_file(str(filepath), str(dest), 
                             conflict_strategy=conflict_strategy, dry_run=True)
                except (FileNotFoundError, ValueError):
                    # Expected errors should not modify filesystem
                    pass
            
            # Verify filesystem unchanged
            final_state = get_all_files(tmppath)
            
            assert initial_state == final_state, "File system changed during dry-run"
    
    @given(
        file_count=st.integers(min_value=1, max_value=15),
        conflict_strategy=st.sampled_from(['skip', 'overwrite', 'rename'])
    )
    @settings(max_examples=100)
    def test_property_metadata_preservation(self, file_count, conflict_strategy):
        """
        **Feature: lazy-automation-tool, Property 8: Metadata preservation invariant**
        
        For any file move operation, the file's metadata (timestamps, permissions)
        should remain identical before and after the move.
        
        **Validates: Requirements 2.5**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            destdir = tmppath / "destination"
            destdir.mkdir()
            
            # Create files and capture their metadata
            files_metadata = []
            for i in range(file_count):
                filepath = tmppath / f"file_{i}.txt"
                filepath.write_text(f"content_{i}")
                
                # Get initial metadata
                metadata_before = get_file_metadata(str(filepath))
                files_metadata.append((filepath, metadata_before))
            
            # Move files (not dry-run)
            moved_files = []
            for filepath, metadata_before in files_metadata:
                dest = destdir / filepath.name
                try:
                    success, actual_dest = move_file(
                        str(filepath), str(dest),
                        conflict_strategy=conflict_strategy,
                        dry_run=False
                    )
                    if success and actual_dest:
                        moved_files.append((actual_dest, metadata_before))
                except (FileNotFoundError, ValueError):
                    pass
            
            # Verify metadata preserved for successfully moved files
            for dest_path, metadata_before in moved_files:
                metadata_after = get_file_metadata(dest_path)
                
                # Check timestamps (allow small tolerance for filesystem precision)
                assert abs((metadata_after['modified'] - metadata_before['modified']).total_seconds()) < 1, \
                    f"Modified time changed for {dest_path}"
                
                # Check permissions
                assert metadata_after['permissions'] == metadata_before['permissions'], \
                    f"Permissions changed for {dest_path}"
    
    @given(
        file_count=st.integers(min_value=5, max_value=30),
        filter_extensions=st.lists(
            st.sampled_from(['.txt', '.py', '.json', '.csv', '.xml', '.md']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_property_extension_filtering_accuracy(self, file_count, filter_extensions):
        """
        **Feature: lazy-automation-tool, Property 4: Extension filtering accuracy**
        
        For any file set and extension filter, only files with matching extensions
        should be included in the operation.
        
        **Validates: Requirements 1.5**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # All possible extensions
            all_extensions = ['.txt', '.py', '.json', '.csv', '.xml', '.md', '.log']
            
            # Create files with various extensions
            created_files = {}
            for i in range(file_count):
                ext = all_extensions[i % len(all_extensions)]
                filepath = tmppath / f"file_{i}{ext}"
                filepath.write_text(f"content_{i}")
                created_files[str(filepath)] = ext
            
            # List files with filter
            filtered_files = list_files(str(tmppath), extensions=filter_extensions)
            
            # Verify all returned files have matching extensions
            for filepath in filtered_files:
                file_ext = Path(filepath).suffix
                assert file_ext in filter_extensions, \
                    f"File {filepath} with extension {file_ext} should not be in filtered results"
            
            # Verify all files with matching extensions are included
            expected_files = [fp for fp, ext in created_files.items() if ext in filter_extensions]
            assert len(filtered_files) == len(expected_files), \
                f"Expected {len(expected_files)} files but got {len(filtered_files)}"
            
            # Verify no files with non-matching extensions are included
            for filepath in filtered_files:
                assert filepath in expected_files, \
                    f"Unexpected file {filepath} in filtered results"
