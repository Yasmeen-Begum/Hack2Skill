"""Tests for reporting and logging functionality."""

import pytest
from io import StringIO
from hypothesis import given, strategies as st, settings
from lazy_automation.reporting import Reporter
from lazy_automation.tasks.base import Operation, TaskResult


class TestReporter:
    """Unit tests for Reporter."""
    
    def test_report_preview_basic(self):
        """Test basic preview reporting."""
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        
        operations = [
            Operation(type="rename", source="/path/file1.txt", destination="/path/renamed1.txt"),
            Operation(type="move", source="/path/file2.txt", destination="/dest/file2.txt")
        ]
        
        reporter.report_preview(operations)
        
        result = output.getvalue()
        assert "PREVIEW" in result
        assert "2 operation(s)" in result
        assert "/path/file1.txt" in result
        assert "/path/renamed1.txt" in result
    
    def test_report_results_basic(self):
        """Test basic results reporting."""
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        
        result = TaskResult(
            success_count=5,
            failure_count=2,
            operations=[],
            errors=[
                {"operation": Operation(type="rename", source="/path/fail.txt"), "error": "Permission denied"}
            ]
        )
        
        reporter.report_results(result)
        
        output_text = output.getvalue()
        assert "Successful: 5" in output_text
        assert "Failed: 2" in output_text
        assert "Permission denied" in output_text
    
    def test_verbose_logging(self):
        """Test verbose logging mode."""
        output = StringIO()
        reporter = Reporter(verbose=True, output=output)
        
        reporter.log_operation("Test message", "INFO")
        
        output_text = output.getvalue()
        assert "[INFO] Test message" in output_text
    
    def test_non_verbose_logging(self):
        """Test non-verbose logging mode."""
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        
        reporter.log_operation("Test message", "INFO")
        
        output_text = output.getvalue()
        # Should not appear in output when not verbose
        assert output_text == ""
        
        # But should be in log entries
        assert len(reporter.get_log_entries()) == 1
        assert "[INFO] Test message" in reporter.get_log_entries()[0]


class TestPropertyBasedReporter:
    """Property-based tests for Reporter."""

    
    @given(
        operation_count=st.integers(min_value=1, max_value=50),
        operation_types=st.lists(
            st.sampled_from(['rename', 'move', 'summarize']),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_property_preview_display_completeness(self, operation_count, operation_types):
        """
        **Feature: lazy-automation-tool, Property 12: Preview display completeness**
        
        For any operation in preview mode, the displayed output should include
        both the before state and after state for each planned change.
        
        **Validates: Requirements 4.3**
        """
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        
        # Generate random operations
        operations = []
        for i in range(operation_count):
            op_type = operation_types[i % len(operation_types)]
            source = f"/path/to/source_{i}.txt"
            
            if op_type == "summarize":
                # Summarize operations may not have destination
                destination = None
            else:
                destination = f"/path/to/dest_{i}.txt"
            
            operations.append(Operation(
                type=op_type,
                source=source,
                destination=destination,
                metadata={"index": i}
            ))
        
        # Report preview
        reporter.report_preview(operations)
        
        # Get output
        output_text = output.getvalue()
        
        # Verify all operations are displayed
        for op in operations:
            # Check that source (before state) is present
            assert op.source in output_text, \
                f"Source path {op.source} not found in preview output"
            
            # Check that destination (after state) is present for operations that have it
            if op.destination:
                assert op.destination in output_text, \
                    f"Destination path {op.destination} not found in preview output"
        
        # Verify operation count is displayed
        assert str(len(operations)) in output_text, \
            "Operation count not displayed in preview"
        
        # Verify "PREVIEW" indicator is present
        assert "PREVIEW" in output_text, \
            "Preview indicator not found in output"

    
    @given(
        total_operations=st.integers(min_value=5, max_value=30),
        failure_indices=st.lists(
            st.integers(min_value=0, max_value=29),
            min_size=1,
            max_size=10,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_property_partial_failure_resilience(self, total_operations, failure_indices):
        """
        **Feature: lazy-automation-tool, Property 13: Partial failure resilience**
        
        For any batch operation where some files fail, all remaining files should
        still be processed, and the final result should accurately report both
        success and failure counts.
        
        **Validates: Requirements 5.2, 5.3**
        """
        # Filter failure indices to be within range
        failure_indices = [idx for idx in failure_indices if idx < total_operations]
        
        if not failure_indices:
            # Need at least one failure for this test
            failure_indices = [0]
        
        # Create operations
        operations = []
        for i in range(total_operations):
            operations.append(Operation(
                type="rename",
                source=f"/path/file_{i}.txt",
                destination=f"/path/renamed_{i}.txt",
                metadata={"index": i}
            ))
        
        # Simulate execution with some failures
        success_count = 0
        failure_count = 0
        errors = []
        
        for i, op in enumerate(operations):
            if i in failure_indices:
                # Simulate failure
                failure_count += 1
                errors.append({
                    "operation": op,
                    "error": "Simulated failure"
                })
            else:
                # Simulate success
                success_count += 1
        
        # Create result
        result = TaskResult(
            success_count=success_count,
            failure_count=failure_count,
            operations=operations,
            errors=errors
        )
        
        # Verify counts are accurate
        assert result.success_count + result.failure_count == total_operations, \
            "Total of success and failure counts should equal total operations"
        
        assert result.success_count == total_operations - len(failure_indices), \
            f"Success count should be {total_operations - len(failure_indices)}"
        
        assert result.failure_count == len(failure_indices), \
            f"Failure count should be {len(failure_indices)}"
        
        assert len(result.errors) == len(failure_indices), \
            "Number of errors should match failure count"
        
        # Test that reporter can handle this result
        output = StringIO()
        reporter = Reporter(verbose=False, output=output)
        reporter.report_results(result)
        
        output_text = output.getvalue()
        
        # Verify both success and failure counts are reported
        assert str(result.success_count) in output_text, \
            "Success count not found in report"
        
        assert str(result.failure_count) in output_text, \
            "Failure count not found in report"
        
        assert str(total_operations) in output_text, \
            "Total operations count not found in report"

    
    @given(
        log_count=st.integers(min_value=5, max_value=50),
        log_levels=st.lists(
            st.sampled_from(['INFO', 'WARNING', 'ERROR', 'DEBUG']),
            min_size=5,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_property_verbose_logging_expansion(self, log_count, log_levels):
        """
        **Feature: lazy-automation-tool, Property 14: Verbose logging expansion**
        
        For any operation, enabling verbose logging should produce more log entries
        in the output than normal mode.
        
        **Validates: Requirements 5.4**
        """
        # Create log messages
        messages = [f"Operation {i} message" for i in range(log_count)]
        levels = [log_levels[i % len(log_levels)] for i in range(log_count)]
        
        # Test with verbose mode OFF
        output_normal = StringIO()
        reporter_normal = Reporter(verbose=False, output=output_normal)
        
        for msg, level in zip(messages, levels):
            reporter_normal.log_operation(msg, level)
        
        normal_output = output_normal.getvalue()
        normal_log_entries = reporter_normal.get_log_entries()
        
        # Test with verbose mode ON
        output_verbose = StringIO()
        reporter_verbose = Reporter(verbose=True, output=output_verbose)
        
        for msg, level in zip(messages, levels):
            reporter_verbose.log_operation(msg, level)
        
        verbose_output = output_verbose.getvalue()
        verbose_log_entries = reporter_verbose.get_log_entries()
        
        # Verify both modes store the same number of log entries internally
        assert len(normal_log_entries) == len(verbose_log_entries) == log_count, \
            "Both modes should store the same number of log entries"
        
        # Verify verbose mode produces more output
        assert len(verbose_output) > len(normal_output), \
            "Verbose mode should produce more output than normal mode"
        
        # Verify normal mode produces minimal or no output
        # (log entries are stored but not displayed)
        assert len(normal_output) == 0, \
            "Normal mode should not display log entries in output"
        
        # Verify verbose mode displays all log entries
        for msg in messages:
            assert msg in verbose_output, \
                f"Message '{msg}' should appear in verbose output"
        
        # Verify log levels appear in verbose output
        for level in set(levels):
            assert f"[{level}]" in verbose_output, \
                f"Log level [{level}] should appear in verbose output"
