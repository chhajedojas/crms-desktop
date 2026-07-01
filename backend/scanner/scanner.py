"""
Main scanner for orchestrating file scanning operations.
"""

import os
import uuid
import time
import threading
from pathlib import Path
from typing import Optional, Callable, List, Dict
from scanner.data_structures import (
    FileInfo,
    ScanConfiguration,
    ScanResult,
    ScanError,
    ScanProgress,
)
from scanner.path_resolver import PathResolver
from scanner.filter_manager import FilterManager
from scanner.file_scanner import FileScanner
from scanner.progress_tracker import ProgressTracker
from scanner.scan_state import ScanStateManager
from scanner.worker_pool import WorkerPool
from core import get_logger


class Scanner:
    """Main scanner for orchestrating file scanning operations."""

    def __init__(self, configuration: ScanConfiguration):
        """
        Initialize scanner.

        Args:
            configuration: Scan configuration
        """
        self.config = configuration
        self.logger = get_logger(__name__)

        # Initialize components
        self.root_path = Path(configuration.root_path)
        self.path_resolver = PathResolver(self.root_path)
        self.filter_manager = FilterManager(
            include_patterns=configuration.include_patterns,
            exclude_patterns=configuration.exclude_patterns,
            include_hidden=configuration.include_hidden,
            include_system=configuration.include_system,
        )
        self.file_scanner = FileScanner(
            root_path=self.root_path,
            enable_hash=configuration.enable_hash,
            chunk_size=configuration.chunk_size,
        )
        self.worker_pool = WorkerPool(
            max_workers=configuration.max_workers,
            queue_size=configuration.queue_size,
        )

        # State management
        self._cancelled = threading.Event()
        self._files: List[FileInfo] = []
        self._duplicates: Dict[str, List[FileInfo]] = {}
        self._errors: List[ScanError] = []
        self._hash_map: Dict[str, List[FileInfo]] = {}
        self._lock = threading.Lock()

        # Progress tracking
        self._progress_tracker: Optional[ProgressTracker] = None

        # Scan state
        self._scan_id = str(uuid.uuid4())
        self._state_manager = ScanStateManager(self.root_path / ".crms_scan_state.json")

    def scan(
        self,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        resume: bool = False,
    ) -> ScanResult:
        """
        Perform file scan.

        Args:
            progress_callback: Optional callback for progress updates
            resume: Whether to resume from previous scan

        Returns:
            ScanResult with scanned files, duplicates, and errors
        """
        start_time = time.time()

        try:
            # Load previous state if resuming
            if resume:
                previous_state = self._state_manager.load()
                if previous_state:
                    self.logger.info(f"Resuming scan from {previous_state.last_checkpoint}")
            else:
                self._state_manager.delete()

            # Initialize progress tracker
            total_files = self._count_files()
            total_bytes = self._estimate_total_bytes()
            self._progress_tracker = ProgressTracker(
                total_files=total_files,
                total_bytes=total_bytes,
                progress_callback=progress_callback,
            )

            # Start worker pool
            self.worker_pool.start()

            # Perform directory traversal and scanning
            self._traverse_and_scan()

            # Wait for completion
            self.worker_pool.wait_for_completion()

            # Complete progress
            if self._progress_tracker:
                self._progress_tracker.complete()

            # Build result
            duration = time.time() - start_time
            result = ScanResult(
                files=self._files,
                duplicates=self._duplicates,
                errors=self._errors,
                duration=duration,
                cancelled=self._cancelled.is_set(),
            )

            self.logger.info(
                f"Scan complete: {len(self._files)} files, "
                f"{len(self._duplicates)} duplicate groups, "
                f"{len(self._errors)} errors, "
                f"{duration:.2f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            raise
        finally:
            self.worker_pool.shutdown()
            self._state_manager.delete()

    def cancel(self):
        """Cancel the current scan."""
        self._cancelled.set()
        self.logger.info("Scan cancellation requested")

    def _count_files(self) -> int:
        """Count total files to scan."""
        count = 0
        for root, dirs, files in os.walk(self.root_path):
            count += len(files)
        return count

    def _estimate_total_bytes(self) -> int:
        """Estimate total bytes to scan."""
        total = 0
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                try:
                    file_path = Path(root) / file
                    total += file_path.stat().st_size
                except OSError:
                    pass
        return total

    def _traverse_and_scan(self):
        """Traverse directory tree and scan files."""
        for root, dirs, files in os.walk(self.root_path):
            # Check for cancellation
            if self._cancelled.is_set():
                break

            root_path = Path(root)

            # Filter directories
            dirs[:] = [d for d in dirs if self._should_include_directory(root_path / d)]

            # Scan files
            for file in files:
                if self._cancelled.is_set():
                    break

                file_path = root_path / file

                if self._should_include_file(file_path):
                    self._submit_file_scan(file_path)

    def _should_include_directory(self, dir_path: Path) -> bool:
        """Check if directory should be included."""
        # Skip if symlink loop
        if self.path_resolver.is_symlink_loop(dir_path):
            return False

        # Skip if outside root
        if not self.path_resolver.is_within_root(dir_path):
            return False

        return True

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included."""
        # Skip if symlink loop
        if self.path_resolver.is_symlink_loop(file_path):
            return False

        # Skip if outside root
        if not self.path_resolver.is_within_root(file_path):
            return False

        # Apply filters
        return self.filter_manager.should_include(file_path)

    def _submit_file_scan(self, file_path: Path):
        """Submit file scan to worker pool."""
        self.worker_pool.submit(self._scan_file_task, file_path)

    def _scan_file_task(self, file_path: Path) -> Optional[FileInfo]:
        """Task for scanning a single file."""
        try:
            # Check for cancellation
            if self._cancelled.is_set():
                return None

            # Scan file
            file_info = self.file_scanner.scan_file(
                file_path,
                cancellation_flag=self._cancelled.is_set,
            )

            # Check for duplicates
            if self.config.enable_duplicate_detection and file_info.hash:
                is_duplicate = self._check_duplicate(file_info)
                file_info.is_duplicate = is_duplicate

            # Add to results
            with self._lock:
                self._files.append(file_info)

            # Update progress
            if self._progress_tracker:
                self._progress_tracker.update(
                    str(file_path),
                    file_info.size,
                    file_info.is_duplicate,
                )

            return file_info

        except Exception as e:
            error = ScanError(
                file_path=str(file_path),
                error_type=type(e).__name__,
                error_message=str(e),
            )
            with self._lock:
                self._errors.append(error)
            self.logger.error(f"Error scanning {file_path}: {str(e)}")
            return None

    def _check_duplicate(self, file_info: FileInfo) -> bool:
        """Check if file is a duplicate."""
        if not file_info.hash:
            return False

        with self._lock:
            if file_info.hash in self._hash_map:
                self._hash_map[file_info.hash].append(file_info)
                self._duplicates[file_info.hash] = self._hash_map[file_info.hash]
                file_info.duplicate_of = self._hash_map[file_info.hash][0].absolute_path
                return True
            else:
                self._hash_map[file_info.hash] = [file_info]
                return False
