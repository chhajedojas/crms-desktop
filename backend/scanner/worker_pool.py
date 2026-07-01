"""
Worker pool for parallel file scanning.
"""

import threading
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from core import get_logger


class WorkerPool:
    """Manages a pool of worker threads for parallel processing."""

    def __init__(self, max_workers: int = 4, queue_size: int = 1000):
        """
        Initialize worker pool.

        Args:
            max_workers: Maximum number of worker threads
            queue_size: Maximum size of work queue
        """
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.logger = get_logger(__name__)

        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: list[Future] = []
        self._lock = threading.Lock()

    def start(self):
        """Start the worker pool."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            self.logger.info(f"Worker pool started with {self.max_workers} workers")

    def submit(self, task: Callable[..., Any], *args, **kwargs) -> Future:
        """
        Submit a task to the worker pool.

        Args:
            task: Callable to execute
            *args: Positional arguments for task
            **kwargs: Keyword arguments for task

        Returns:
            Future object for the task
        """
        if self._executor is None:
            raise RuntimeError("Worker pool not started")

        future = self._executor.submit(task, *args, **kwargs)

        with self._lock:
            self._futures.append(future)

        return future

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all submitted tasks to complete.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            True if all tasks completed, False if timeout
        """
        if self._executor is None:
            return True

        try:
            with self._lock:
                for future in self._futures:
                    future.result(timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for task completion: {str(e)}")
            return False

    def shutdown(self, wait: bool = True):
        """
        Shutdown the worker pool.

        Args:
            wait: Whether to wait for tasks to complete
        """
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None
            self._futures.clear()
            self.logger.info("Worker pool shut down")

    def active_count(self) -> int:
        """
        Get number of active workers.

        Returns:
            Number of active workers
        """
        if self._executor is None:
            return 0
        return len(self._futures)
