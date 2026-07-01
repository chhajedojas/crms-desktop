"""
Data structures for the scanner module.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set


@dataclass
class FileInfo:
    """Information about a scanned file."""

    absolute_path: str
    relative_path: str
    filename: str
    extension: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    permissions: int
    hash: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None


@dataclass
class ScanProgress:
    """Progress information for a scan."""

    total_files: int
    scanned_files: int
    total_bytes: int
    scanned_bytes: int
    duplicates_found: int
    current_file: Optional[str] = None
    percentage: float = 0.0


@dataclass
class ScanError:
    """Error information for a scan."""

    file_path: str
    error_type: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScanResult:
    """Result of a scan operation."""

    files: List[FileInfo]
    duplicates: Dict[str, List[FileInfo]]
    errors: List[ScanError]
    duration: float
    cancelled: bool


@dataclass
class ScanConfiguration:
    """Configuration for scan operations."""

    root_path: str
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    include_hidden: bool = False
    include_system: bool = False
    follow_symlinks: bool = False
    max_workers: int = 4
    chunk_size: int = 65536  # 64KB
    queue_size: int = 1000
    checkpoint_interval: int = 1000  # files
    enable_hash: bool = True
    enable_duplicate_detection: bool = True


@dataclass
class ScanState:
    """State for resuming interrupted scans."""

    scan_id: str
    root_path: str
    completed_files: Set[str] = field(default_factory=set)
    last_checkpoint: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    configuration: Optional[ScanConfiguration] = None
