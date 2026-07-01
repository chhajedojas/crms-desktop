"""
Scanner package for CRMS (production refactored version).

This package provides file scanning capabilities with:
- Producer-consumer architecture for proper synchronization
- Streaming results for memory efficiency
- Single-pass directory traversal
- Real checkpointing for resume
- Thread-safe duplicate detection
- Graceful cancellation

Version: 2.0 (Production Refactor)
"""

from scanner.scanner_v2 import ScannerV2
from scanner.data_structures import (
    FileInfo,
    ScanConfiguration,
    ScanResult,
    ScanProgress,
    ScanError,
    ScanState,
)
from scanner.hash_generator import HashGenerator, HashGenerationError
from scanner.path_resolver import PathResolver, PathResolutionError
from scanner.filter_manager import FilterManager
from scanner.file_scanner import FileScanner
from scanner.progress_tracker import ProgressTracker
from scanner.scan_state import ScanStateManager
from scanner.worker_pool import WorkerPool

__all__ = [
    "ScannerV2",
    "FileInfo",
    "ScanConfiguration",
    "ScanResult",
    "ScanProgress",
    "ScanError",
    "ScanState",
    "HashGenerator",
    "HashGenerationError",
    "PathResolver",
    "PathResolutionError",
    "FilterManager",
    "FileScanner",
    "ProgressTracker",
    "ScanStateManager",
    "WorkerPool",
]
