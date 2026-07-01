"""
Unit tests for scanner data structures.
"""

import pytest
from datetime import datetime
from scanner.data_structures import (
    FileInfo,
    ScanProgress,
    ScanError,
    ScanResult,
    ScanConfiguration,
    ScanState,
)


class TestFileInfo:
    """Tests for FileInfo dataclass."""

    def test_init(self):
        """Test initialization."""
        file_info = FileInfo(
            absolute_path="/path/to/file.txt",
            relative_path="file.txt",
            filename="file.txt",
            extension=".txt",
            mime_type="text/plain",
            size=100,
            created_time=datetime.now(),
            modified_time=datetime.now(),
            permissions=644,
        )
        assert file_info.absolute_path == "/path/to/file.txt"
        assert file_info.hash is None
        assert not file_info.is_duplicate

    def test_init_with_hash(self):
        """Test initialization with hash."""
        file_info = FileInfo(
            absolute_path="/path/to/file.txt",
            relative_path="file.txt",
            filename="file.txt",
            extension=".txt",
            mime_type="text/plain",
            size=100,
            created_time=datetime.now(),
            modified_time=datetime.now(),
            permissions=644,
            hash="abc123",
        )
        assert file_info.hash == "abc123"


class TestScanProgress:
    """Tests for ScanProgress dataclass."""

    def test_init(self):
        """Test initialization."""
        progress = ScanProgress(
            total_files=100,
            scanned_files=50,
            total_bytes=1000000,
            scanned_bytes=500000,
            duplicates_found=5,
        )
        assert progress.total_files == 100
        assert progress.scanned_files == 50
        # percentage is calculated on demand, not stored
        assert progress.percentage == 0.0


class TestScanError:
    """Tests for ScanError dataclass."""

    def test_init(self):
        """Test initialization."""
        error = ScanError(
            file_path="/path/to/file.txt",
            error_type="IOError",
            error_message="File not found",
        )
        assert error.file_path == "/path/to/file.txt"
        assert error.error_type == "IOError"
        assert isinstance(error.timestamp, datetime)


class TestScanResult:
    """Tests for ScanResult dataclass."""

    def test_init(self):
        """Test initialization."""
        result = ScanResult(
            files=[],
            duplicates={},
            errors=[],
            duration=10.5,
            cancelled=False,
        )
        assert result.duration == 10.5
        assert not result.cancelled


class TestScanConfiguration:
    """Tests for ScanConfiguration dataclass."""

    def test_init_default(self):
        """Test initialization with defaults."""
        config = ScanConfiguration(root_path="/path/to/scan")
        assert config.root_path == "/path/to/scan"
        assert config.include_patterns == []
        assert config.include_hidden is False
        assert config.max_workers == 4

    def test_init_custom(self):
        """Test initialization with custom values."""
        config = ScanConfiguration(
            root_path="/path/to/scan",
            include_patterns=["*.txt"],
            exclude_patterns=["*.tmp"],
            include_hidden=True,
            max_workers=8,
        )
        assert "*.txt" in config.include_patterns
        assert config.include_hidden
        assert config.max_workers == 8


class TestScanState:
    """Tests for ScanState dataclass."""

    def test_init(self):
        """Test initialization."""
        state = ScanState(
            scan_id="test-scan-id",
            root_path="/path/to/scan",
        )
        assert state.scan_id == "test-scan-id"
        assert len(state.completed_files) == 0
        assert isinstance(state.last_checkpoint, datetime)
