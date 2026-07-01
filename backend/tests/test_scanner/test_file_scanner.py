"""
Unit tests for file scanner.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from scanner.file_scanner import FileScanner
from scanner.data_structures import FileInfo


class TestFileScanner:
    """Tests for FileScanner class."""

    def test_init(self):
        """Test initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=True)
            assert scanner.root_path == root
            assert scanner.enable_hash
            assert scanner.hash_generator is not None

    def test_init_no_hash(self):
        """Test initialization without hash generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=False)
            assert not scanner.enable_hash
            assert scanner.hash_generator is None

    def test_scan_file(self):
        """Test scanning a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=False)

            test_file = root / "test.txt"
            test_file.write_text("test content")

            file_info = scanner.scan_file(test_file)

            assert isinstance(file_info, FileInfo)
            assert file_info.filename == "test.txt"
            assert file_info.extension == ".txt"
            assert file_info.size > 0
            assert file_info.mime_type
            assert isinstance(file_info.created_time, datetime)
            assert isinstance(file_info.modified_time, datetime)
            assert file_info.permissions > 0

    def test_scan_file_with_hash(self):
        """Test scanning a file with hash generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=True)

            test_file = root / "test.txt"
            test_file.write_text("test content")

            file_info = scanner.scan_file(test_file)

            assert file_info.hash
            assert len(file_info.hash) == 64

    def test_scan_file_nonexistent(self):
        """Test scanning nonexistent file raises IOError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=False)

            nonexistent = root / "nonexistent.txt"
            with pytest.raises(IOError):
                scanner.scan_file(nonexistent)

    def test_scan_file_with_cancellation(self):
        """Test scanning file with cancellation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scanner = FileScanner(root, enable_hash=False)

            test_file = root / "test.txt"
            test_file.write_text("test content")

            cancellation_flag = lambda: True
            with pytest.raises(IOError):
                scanner.scan_file(test_file, cancellation_flag)
