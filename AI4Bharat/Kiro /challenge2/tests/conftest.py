"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from hypothesis import settings


# Configure Hypothesis to run at least 100 iterations
settings.register_profile("default", max_examples=100)
settings.load_profile("default")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    files = []
    
    # Create some text files
    for i in range(5):
        file_path = temp_dir / f"file_{i}.txt"
        file_path.write_text(f"Sample content {i}\n" * 10)
        files.append(file_path)
    
    # Create some other file types
    (temp_dir / "document.pdf").touch()
    (temp_dir / "image.jpg").touch()
    (temp_dir / "data.json").write_text('{"key": "value"}')
    
    files.extend([
        temp_dir / "document.pdf",
        temp_dir / "image.jpg",
        temp_dir / "data.json"
    ])
    
    return files
