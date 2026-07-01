"""
Unit tests for progress tracker.
"""

import pytest
from scanner.progress_tracker import ProgressTracker
from scanner.data_structures import ScanProgress


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_init(self):
        """Test initialization."""
        tracker = ProgressTracker(total_files=100, total_bytes=1000000)
        assert tracker.total_files == 100
        assert tracker.total_bytes == 1000000
        assert tracker._scanned_files == 0
        assert tracker._scanned_bytes == 0

    def test_update(self):
        """Test updating progress."""
        tracker = ProgressTracker(total_files=100, total_bytes=1000000)
        tracker.update("file1.txt", 1000)
        assert tracker._scanned_files == 1
        assert tracker._scanned_bytes == 1000

    def test_update_duplicate(self):
        """Test updating progress with duplicate."""
        tracker = ProgressTracker(total_files=100, total_bytes=1000000)
        tracker.update("file1.txt", 1000, is_duplicate=True)
        assert tracker._scanned_files == 1
        assert tracker._scanned_bytes == 1000
        assert tracker._duplicates_found == 1

    def test_get_progress(self):
        """Test getting progress."""
        tracker = ProgressTracker(total_files=100, total_bytes=1000000)
        tracker.update("file1.txt", 1000)
        progress = tracker.get_progress()
        assert isinstance(progress, ScanProgress)
        assert progress.scanned_files == 1
        assert progress.scanned_bytes == 1000
        assert progress.percentage == 1.0

    def test_get_progress_zero_total(self):
        """Test getting progress with zero total."""
        tracker = ProgressTracker(total_files=0, total_bytes=0)
        progress = tracker.get_progress()
        assert progress.percentage == 0.0

    def test_callback_invoked(self):
        """Test callback is invoked on interval."""
        callback_called = []

        def callback(progress):
            callback_called.append(progress)

        tracker = ProgressTracker(
            total_files=100, total_bytes=1000000, progress_callback=callback, callback_interval=1
        )
        tracker.update("file1.txt", 1000)
        assert len(callback_called) == 1

    def test_complete(self):
        """Test completing scan."""
        callback_called = []

        def callback(progress):
            callback_called.append(progress)

        tracker = ProgressTracker(total_files=100, total_bytes=1000000, progress_callback=callback)
        tracker.complete()
        assert len(callback_called) == 1
