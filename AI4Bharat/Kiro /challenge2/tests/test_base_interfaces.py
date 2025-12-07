"""Tests for base interfaces and data models."""

import pytest
from datetime import datetime
from lazy_automation.tasks.base import Operation, TaskResult, FileStats, TaskModule


class TestDataModels:
    """Test the core data models."""
    
    def test_operation_creation(self):
        """Test Operation dataclass creation."""
        op = Operation(type="rename", source="/path/to/file.txt", destination="/path/to/new.txt")
        assert op.type == "rename"
        assert op.source == "/path/to/file.txt"
        assert op.destination == "/path/to/new.txt"
        assert op.metadata == {}
    
    def test_operation_with_metadata(self):
        """Test Operation with custom metadata."""
        op = Operation(
            type="move",
            source="/src/file.txt",
            destination="/dst/file.txt",
            metadata={"conflict_strategy": "skip"}
        )
        assert op.metadata["conflict_strategy"] == "skip"
    
    def test_task_result_creation(self):
        """Test TaskResult dataclass creation."""
        op = Operation(type="rename", source="/file.txt", destination="/new.txt")
        result = TaskResult(
            success_count=5,
            failure_count=2,
            operations=[op],
            errors=[{"operation": op, "error": "Permission denied"}]
        )
        assert result.success_count == 5
        assert result.failure_count == 2
        assert len(result.operations) == 1
        assert len(result.errors) == 1
    
    def test_file_stats_creation(self):
        """Test FileStats dataclass creation."""
        now = datetime.now()
        stats = FileStats(
            path="/path/to/file.txt",
            size_bytes=1024,
            line_count=50,
            word_count=200,
            format="txt",
            created=now,
            modified=now
        )
        assert stats.path == "/path/to/file.txt"
        assert stats.size_bytes == 1024
        assert stats.line_count == 50
        assert stats.word_count == 200
        assert stats.format == "txt"


class TestTaskModuleInterface:
    """Test the TaskModule abstract base class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that TaskModule cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TaskModule()
    
    def test_concrete_implementation(self):
        """Test that concrete implementations must implement abstract methods."""
        
        class ConcreteTask(TaskModule):
            def plan(self, directory, options):
                return []
            
            def execute(self, operations, dry_run=False):
                return TaskResult(
                    success_count=0,
                    failure_count=0,
                    operations=[],
                    errors=[]
                )
        
        task = ConcreteTask()
        assert task.plan("/test", {}) == []
        result = task.execute([])
        assert result.success_count == 0
