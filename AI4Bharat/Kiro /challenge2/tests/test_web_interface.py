"""Tests for the Gradio web interface."""

import pytest
from pathlib import Path
import tempfile
import shutil

from lazy_automation.web_interface import WebInterface


class TestWebInterface:
    """Test suite for the web interface."""
    
    def test_interface_creation(self):
        """Test that the interface can be created."""
        web_interface = WebInterface()
        interface = web_interface.create_interface()
        
        assert interface is not None
        assert hasattr(interface, 'launch')
    
    def test_handle_rename_missing_directory(self):
        """Test rename handler with missing directory."""
        web_interface = WebInterface()
        
        result = web_interface._handle_rename(
            directory="",
            pattern="file_{n}.txt",
            extensions="",
            dry_run=True
        )
        
        assert "Error" in result
        assert "required" in result.lower()
    
    def test_handle_rename_missing_pattern(self):
        """Test rename handler with missing pattern."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = web_interface._handle_rename(
                directory=tmpdir,
                pattern="",
                extensions="",
                dry_run=True
            )
            
            assert "Error" in result
            assert "pattern" in result.lower()
    
    def test_handle_rename_nonexistent_directory(self):
        """Test rename handler with nonexistent directory."""
        web_interface = WebInterface()
        
        result = web_interface._handle_rename(
            directory="/nonexistent/path/12345",
            pattern="file_{n}.txt",
            extensions="",
            dry_run=True
        )
        
        assert "Error" in result
        assert "not found" in result.lower()
    
    def test_handle_rename_success(self):
        """Test successful rename operation in dry-run mode."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("content1")
            (test_dir / "file2.txt").write_text("content2")
            
            result = web_interface._handle_rename(
                directory=str(test_dir),
                pattern="renamed_{n}.txt",
                extensions=".txt",
                dry_run=True
            )
            
            assert "Preview Complete" in result
            assert "2" in result  # Should show 2 files
    
    def test_handle_organize_missing_directory(self):
        """Test organize handler with missing directory."""
        web_interface = WebInterface()
        
        result = web_interface._handle_organize(
            directory="",
            rule_type="type",
            conflict_strategy="skip",
            dry_run=True
        )
        
        assert "Error" in result
        assert "required" in result.lower()
    
    def test_handle_organize_success(self):
        """Test successful organize operation in dry-run mode."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_dir = Path(tmpdir)
            (test_dir / "doc.pdf").write_text("content")
            (test_dir / "image.jpg").write_text("content")
            
            result = web_interface._handle_organize(
                directory=str(test_dir),
                rule_type="type",
                conflict_strategy="skip",
                dry_run=True
            )
            
            assert "Preview Complete" in result
            assert "2" in result  # Should show 2 files
    
    def test_handle_summarize_missing_directory(self):
        """Test summarize handler with missing directory."""
        web_interface = WebInterface()
        
        result, download = web_interface._handle_summarize(
            directory="",
            extensions="",
            output_file=""
        )
        
        assert "Error" in result
        assert "required" in result.lower()
        assert download is None
    
    def test_handle_summarize_success(self):
        """Test successful summarize operation."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("Hello world\nSecond line")
            (test_dir / "file2.txt").write_text("Another file")
            
            result, download = web_interface._handle_summarize(
                directory=str(test_dir),
                extensions=".txt",
                output_file=""
            )
            
            assert "Summary Complete" in result
            assert "2" in result  # Should show 2 files analyzed
            assert download is None  # No output file specified
    
    def test_handle_summarize_with_output_file(self):
        """Test summarize with output file."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("Hello world")
            
            output_file = str(test_dir / "summary.txt")
            
            result, download = web_interface._handle_summarize(
                directory=str(test_dir),
                extensions=".txt",
                output_file=output_file
            )
            
            assert "Summary Complete" in result
            assert "saved" in result.lower()
            assert download == output_file
            assert Path(output_file).exists()
    
    def test_extension_parsing(self):
        """Test that extensions are parsed correctly."""
        web_interface = WebInterface()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files with different extensions
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("content")
            (test_dir / "file2.pdf").write_text("content")
            (test_dir / "file3.jpg").write_text("content")
            
            # Test with extensions that have dots
            result = web_interface._handle_rename(
                directory=str(test_dir),
                pattern="renamed_{n}.txt",
                extensions=".txt,.pdf",  # With dots
                dry_run=True
            )
            
            assert "Preview Complete" in result
            assert "2" in result  # Should only match .txt and .pdf
            
            # Test with extensions without dots
            result = web_interface._handle_rename(
                directory=str(test_dir),
                pattern="renamed_{n}.txt",
                extensions="txt,pdf",  # Without dots
                dry_run=True
            )
            
            assert "Preview Complete" in result
            assert "2" in result  # Should still work
