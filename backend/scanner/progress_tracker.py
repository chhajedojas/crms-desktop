"""
Progress tracker for tracking scan progress and invoking callbacks.
"""

import threading
from typing import Optional, Callable
from scanner.data_structures import ScanProgress
from core import get_logger


class ProgressTracker:
    """Tracks scan progress and invokes callbacks."""

    def __init__(
        self,
        total_files: int,
        total_bytes: int,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        callback_interval: int = 100,
    ):
        """
        Initialize progress tracker.

        Args:
            total_files: Total number of files to scan
            total_bytes: Total bytes to scan
            progress_callback: Optional callback for progress updates
            callback_interval: Number of files between callbacks
        """
        self.total_files = total_files
        self.total_bytes = total_bytes
        self.progress_callback = progress_callback
        self.callback_interval = callback_interval
        self.logger = get_logger(__name__)

        self._scanned_files = 0
        self._scanned_bytes = 0
        self._duplicates_found = 0
        self._current_file: Optional[str] = None
        self._lock = threading.Lock()

    def update(self, file_path: str, file_size: int, is_duplicate: bool = False):
        """
        Update progress for a scanned file.

        Args:
            file_path: Path to scanned file
            file_size: Size of scanned file
            is_duplicate: Whether file is a duplicate
        """
        with self._lock:
            self._scanned_files += 1
            self._scanned_bytes += file_size
            self._current_file = file_path

            if is_duplicate:
                self._duplicates_found += 1

            # Invoke callback if interval reached
            if self._scanned_files % self.callback_interval == 0:
                self._invoke_callback()

    def _invoke_callback(self):
        """Invoke progress callback if configured."""
        if self.progress_callback:
            progress = self.get_progress()
            try:
                self.progress_callback(progress)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {str(e)}")

    def get_progress(self) -> ScanProgress:
        """
        Get current progress.

        Returns:
            ScanProgress object
        """
        with self._lock:
            percentage = (
                (self._scanned_files / self.total_files * 100) if self.total_files > 0 else 0.0
            )
            return ScanProgress(
                total_files=self.total_files,
                scanned_files=self._scanned_files,
                total_bytes=self.total_bytes,
                scanned_bytes=self._scanned_bytes,
                duplicates_found=self._duplicates_found,
                current_file=self._current_file,
                percentage=percentage,
            )

    def complete(self):
        """Mark scan as complete and invoke final callback."""
        with self._lock:
            self._invoke_callback()
            self.logger.info(
                f"Scan complete: {self._scanned_files}/{self.total_files} files, "
                f"{self._duplicates_found} duplicates"
            )
