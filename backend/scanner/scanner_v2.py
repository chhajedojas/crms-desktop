"""
Scanner V2 - Production refactored version.

This version addresses all critical issues from the engineering review:
1. Producer-consumer architecture for proper synchronization
2. Streaming results for memory efficiency
3. Single-pass directory traversal
4. Real checkpointing for resume
5. Graceful cancellation
6. Thread-safe duplicate detection
"""

import os
import uuid
import time
import threading
import queue
from pathlib import Path
from typing import Optional, Callable, Dict, Set
from scanner.data_structures import (
    FileInfo,
    ScanConfiguration,
    ScanResult,
    ScanError,
    ScanProgress,
    ScanState,
)
from scanner.path_resolver import PathResolver
from scanner.filter_manager import FilterManager
from scanner.file_scanner import FileScanner
from scanner.hash_generator import HashGenerationError
from scanner.scan_state import ScanStateManager
from core import get_logger


class ScannerV2:
    """
    Production-ready scanner with producer-consumer architecture.

    This scanner uses a proper producer-consumer pattern where:
    - Producer: Directory traversal discovers files and queues them
    - Consumers: Worker threads process files from the queue
    - Results: Streamed via callback, not stored in memory
    """

    def __init__(self, configuration: ScanConfiguration):
        """
        Initialize scanner V2.

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

        # Producer-consumer architecture
        self._file_queue: queue.Queue = queue.Queue(maxsize=configuration.queue_size)
        self._num_workers = configuration.max_workers
        self._workers: list[threading.Thread] = []
        self._producer_thread: Optional[threading.Thread] = None

        # State management
        self._cancelled = threading.Event()
        self._errors: list[ScanError] = []
        self._duplicates: Dict[str, Set[str]] = {}  # hash -> set of file paths
        self._duplicate_lock = threading.Lock()
        self._scan_complete = threading.Event()
        self._active_workers = 0
        self._worker_lock = threading.Lock()

        # Progress tracking
        self._total_files = 0
        self._scanned_files = 0
        self._total_bytes = 0
        self._scanned_bytes = 0
        self._duplicates_found = 0
        self._progress_lock = threading.Lock()
        self._progress_callback: Optional[Callable[[ScanProgress], None]] = None
        self._progress_interval = 100

        # Checkpointing
        self._scan_id = str(uuid.uuid4())
        self._state_manager = ScanStateManager(self.root_path / ".crms_scan_state_v2.json")
        self._completed_files: Set[str] = set()
        self._checkpoint_interval = configuration.checkpoint_interval
        self._last_checkpoint_count = 0

        # Result streaming
        self._result_callback: Optional[Callable[[FileInfo], None]] = None

    def scan(
        self,
        result_callback: Optional[Callable[[FileInfo], None]] = None,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        resume: bool = False,
    ) -> ScanResult:
        """
        Perform file scan with streaming results.

        Args:
            result_callback: Callback for each scanned file (streaming)
            progress_callback: Callback for progress updates
            resume: Whether to resume from previous scan

        Returns:
            ScanResult with statistics (files not stored in memory)
        """
        self._result_callback = result_callback
        self._progress_callback = progress_callback

        start_time = time.time()

        try:
            # Load previous state if resuming
            if resume:
                previous_state = self._state_manager.load()
                if previous_state:
                    self._completed_files = previous_state.completed_files
                    self.logger.info(
                        f"Resuming scan: {len(self._completed_files)} files already completed"
                    )
            else:
                self._state_manager.delete()
                self._completed_files.clear()

            # Start producer thread
            self._producer_thread = threading.Thread(target=self._producer, daemon=True)
            self._producer_thread.start()

            # Start consumer threads
            self._start_consumers()

            # Wait for completion
            self._scan_complete.wait(timeout=300)  # 5 minute timeout

            # Complete progress
            self._update_progress(final=True)

            # Save final state
            self._save_checkpoint()

            # Build result (statistics only, no files in memory)
            duration = time.time() - start_time
            result = ScanResult(
                files=[],  # Empty - files streamed via callback
                duplicates={},  # Empty - not stored in memory
                errors=self._errors,
                duration=duration,
                cancelled=self._cancelled.is_set(),
            )

            self.logger.info(
                f"Scan complete: {self._scanned_files} files scanned, "
                f"{self._duplicates_found} duplicates, "
                f"{len(self._errors)} errors, "
                f"{duration:.2f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            raise
        finally:
            self._shutdown()

    def cancel(self):
        """Cancel the current scan gracefully."""
        self._cancelled.set()
        self.logger.info("Scan cancellation requested")

    def _start_consumers(self):
        """Start consumer worker threads."""
        for i in range(self._num_workers):
            worker = threading.Thread(target=self._consumer, daemon=True, name=f"Worker-{i}")
            worker.start()
            self._workers.append(worker)

    def _producer(self):
        """Producer thread: discovers files and queues them."""
        try:
            self.logger.info("Producer thread started")

            # Single-pass directory traversal
            for root, dirs, files in os.walk(self.root_path):
                if self._cancelled.is_set():
                    break

                root_path = Path(root)

                # Filter directories
                dirs[:] = [d for d in dirs if self._should_include_directory(root_path / d)]

                # Process files
                for file in files:
                    if self._cancelled.is_set():
                        break

                    file_path = root_path / file

                    if self._should_include_file(file_path):
                        # Check if already completed (resume)
                        file_key = str(file_path.resolve())
                        if file_key in self._completed_files:
                            self.logger.debug(f"Skipping already completed: {file_path}")
                            continue

                        # Update total count
                        with self._progress_lock:
                            self._total_files += 1
                            try:
                                self._total_bytes += file_path.stat().st_size
                            except OSError:
                                pass

                        # Queue file for processing
                        try:
                            self._file_queue.put(file_path, timeout=1.0)
                        except queue.Full:
                            self.logger.warning("File queue full, waiting...")
                            self._file_queue.put(file_path)

            # Signal completion (send sentinel for each worker)
            for _ in range(self._num_workers):
                self._file_queue.put(None)

            self.logger.info("Producer thread finished")

        except Exception as e:
            self.logger.error(f"Producer thread error: {str(e)}")
            self._errors.append(
                ScanError(
                    file_path="producer",
                    error_type="ProducerError",
                    error_message=str(e),
                )
            )

    def _consumer(self):
        """Consumer thread: processes files from queue."""
        try:
            with self._worker_lock:
                self._active_workers += 1

            while True:
                if self._cancelled.is_set():
                    break

                try:
                    file_path = self._file_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Sentinel for shutdown
                if file_path is None:
                    break

                # Process file
                try:
                    self._process_file(file_path)
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    self._errors.append(
                        ScanError(
                            file_path=str(file_path),
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )

        except Exception as e:
            self.logger.error(f"Consumer thread error: {str(e)}")
        finally:
            with self._worker_lock:
                self._active_workers -= 1
                if self._active_workers == 0:
                    self._scan_complete.set()

    def _process_file(self, file_path: Path):
        """Process a single file and stream result."""
        is_duplicate = False

        try:
            # Scan file
            file_info = self.file_scanner.scan_file(
                file_path,
                cancellation_flag=lambda: self._cancelled.is_set(),
            )

            # Check for duplicates (thread-safe)
            if self.config.enable_duplicate_detection and file_info.hash:
                is_duplicate = self._check_duplicate_threadsafe(file_info)
                file_info.is_duplicate = is_duplicate

            # Stream result via callback
            if self._result_callback:
                self._result_callback(file_info)

            # Mark as completed
            file_key = str(file_path.resolve())
            with self._progress_lock:
                self._completed_files.add(file_key)
                self._scanned_files += 1
                self._scanned_bytes += file_info.size
                if is_duplicate:
                    self._duplicates_found += 1

                # Checkpoint
                self._last_checkpoint_count += 1
                if self._last_checkpoint_count >= self._checkpoint_interval:
                    self._save_checkpoint()
                    self._last_checkpoint_count = 0

            # Update progress
            self._update_progress()

        except HashGenerationError as e:
            if "cancelled" in str(e).lower():
                # Cancellation during hash generation
                return
            raise
        except IOError as e:
            self.logger.warning(f"IO error scanning {file_path}: {str(e)}")
            self._errors.append(
                ScanError(
                    file_path=str(file_path),
                    error_type="IOError",
                    error_message=str(e),
                )
            )
            return
        except Exception as e:
            self.logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            raise

    def _check_duplicate_threadsafe(self, file_info: FileInfo) -> bool:
        """Thread-safe duplicate detection."""
        if not file_info.hash:
            return False

        with self._duplicate_lock:
            if file_info.hash in self._duplicates:
                self._duplicates[file_info.hash].add(str(file_info.absolute_path))
                return True
            else:
                self._duplicates[file_info.hash] = {str(file_info.absolute_path)}
                return False

    def _should_include_directory(self, dir_path: Path) -> bool:
        """Check if directory should be included."""
        if self.path_resolver.is_symlink_loop(dir_path):
            return False
        return self.path_resolver.is_within_root(dir_path)

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included."""
        if self.path_resolver.is_symlink_loop(file_path):
            return False
        if not self.path_resolver.is_within_root(file_path):
            return False
        return self.filter_manager.should_include(file_path)

    def _update_progress(self, final: bool = False):
        """Update progress and invoke callback."""
        with self._progress_lock:
            if final or self._scanned_files % self._progress_interval == 0:
                if self._progress_callback:
                    percentage = (
                        (self._scanned_files / self._total_files * 100)
                        if self._total_files > 0
                        else 0.0
                    )
                    progress = ScanProgress(
                        total_files=self._total_files,
                        scanned_files=self._scanned_files,
                        total_bytes=self._total_bytes,
                        scanned_bytes=self._scanned_bytes,
                        duplicates_found=self._duplicates_found,
                        percentage=percentage,
                    )
                    try:
                        self._progress_callback(progress)
                    except Exception as e:
                        self.logger.error(f"Error in progress callback: {str(e)}")

    def _save_checkpoint(self):
        """Save checkpoint state."""
        try:
            state = ScanState(
                scan_id=self._scan_id,
                root_path=str(self.root_path),
                completed_files=self._completed_files,
                configuration=self.config,
            )
            self._state_manager.save(state)
            self.logger.debug(f"Checkpoint saved: {len(self._completed_files)} files completed")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {str(e)}")

    def _shutdown(self):
        """Shutdown scanner and all threads."""
        self._cancelled.set()

        # Wait for producer
        if self._producer_thread and self._producer_thread.is_alive():
            self._producer_thread.join(timeout=5.0)

        # Wait for consumers
        for worker in self._workers:
            if worker.is_alive():
                worker.join(timeout=5.0)

        self.logger.info("Scanner shutdown complete")
