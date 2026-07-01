"""
Validation tests for scanner edge cases and correctness.
"""

import pytest
import tempfile
import os
from pathlib import Path
from scanner import Scanner, ScanConfiguration
from scanner.data_structures import FileInfo


class TestScannerCorrectness:
    """Tests for scanner correctness with edge cases."""

    def test_empty_directory(self):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ScanConfiguration(root_path=tmpdir, enable_hash=False)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 0
            assert len(result.errors) == 0
            assert not result.cancelled

    def test_single_file(self):
        """Test scanning single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert result.files[0].filename == "test.txt"
            assert result.files[0].size == 12

    def test_nested_directories(self):
        """Test scanning nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "level1" / "level2" / "level3").mkdir(parents=True)
            (root / "level1" / "level2" / "level3" / "test.txt").write_text("test")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert "level3" in result.files[0].relative_path

    def test_hidden_files_excluded(self):
        """Test hidden files are excluded by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".hidden").write_text("hidden")
            (root / "visible.txt").write_text("visible")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False, include_hidden=False)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert result.files[0].filename == "visible.txt"

    def test_hidden_files_included(self):
        """Test hidden files are included when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".hidden").write_text("hidden")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False, include_hidden=True)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert result.files[0].filename == ".hidden"

    def test_duplicate_files_detection(self):
        """Test duplicate file detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            content = "duplicate content"
            (root / "file1.txt").write_text(content)
            (root / "file2.txt").write_text(content)

            config = ScanConfiguration(root_path=tmpdir, enable_hash=True, enable_duplicate_detection=True)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 2
            assert len(result.duplicates) == 1

    def test_unicode_filenames(self):
        """Test scanning files with Unicode names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create file with Unicode name
            (root / "文件.txt").write_text("test")
            (root / "файл.txt").write_text("test")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False)
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 2

    def test_include_pattern(self):
        """Test include pattern filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.txt").write_text("test")
            (root / "test.pdf").write_text("test")
            (root / "other.doc").write_text("test")

            config = ScanConfiguration(
                root_path=tmpdir, enable_hash=False, include_patterns=["*.txt"]
            )
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert result.files[0].filename == "test.txt"

    def test_exclude_pattern(self):
        """Test exclude pattern filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.txt").write_text("test")
            (root / "test.tmp").write_text("test")

            config = ScanConfiguration(
                root_path=tmpdir, enable_hash=False, exclude_patterns=["*.tmp"]
            )
            scanner = Scanner(config)
            result = scanner.scan()

            assert len(result.files) == 1
            assert result.files[0].filename == "test.txt"

    def test_cancellation(self):
        """Test scan cancellation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create many files
            for i in range(100):
                (root / f"file{i}.txt").write_text("test")

            config = ScanConfiguration(root_path=tmpdir, enable_hash=False, max_workers=1)
            scanner = Scanner(config)

            # Cancel after a short delay
            import threading

            def cancel_after_delay():
                import time
                time.sleep(0.01)
                scanner.cancel()

            cancel_thread = threading.Thread(target=cancel_after_delay)
            cancel_thread.start()

            result = scanner.scan()
            cancel_thread.join()

            assert result.cancelled
