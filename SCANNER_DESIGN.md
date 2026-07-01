# Scanner Design Document

**Date:** 2024-01-01
**Milestone:** v0.3 - Scanner
**Status:** Design Phase

---

## Overview

The Scanner module is responsible for discovering files in the file system. It performs recursive directory traversal, collects file metadata, computes SHA-256 hashes using streaming, and detects duplicates. The scanner is designed to handle 500,000+ files efficiently with parallel processing, cancellation support, and resume functionality.

---

## Architecture

### Components

```
scanner/
├── __init__.py
├── scanner.py              # Main scanner class
├── file_scanner.py         # Single file scanner
├── hash_generator.py       # SHA-256 streaming hash
├── path_resolver.py        # Path resolution and validation
├── filter_manager.py       # Include/exclude filters
├── progress_tracker.py     # Progress tracking
├── scan_state.py          # Scan state for resume
└── worker_pool.py         # Parallel processing pool
```

### Component Responsibilities

#### 1. Scanner (scanner.py)
- Orchestrates the scanning process
- Manages worker pool
- Handles cancellation
- Manages resume state
- Coordinates progress callbacks

#### 2. File Scanner (file_scanner.py)
- Scans a single file
- Collects file metadata
- Delegates hash generation
- Returns file info object

#### 3. Hash Generator (hash_generator.py)
- Computes SHA-256 hash using streaming
- Never loads entire file into memory
- Supports cancellation during hashing

#### 4. Path Resolver (path_resolver.py)
- Resolves absolute and relative paths
- Detects symbolic link loops
- Validates paths
- Handles path normalization

#### 5. Filter Manager (filter_manager.py)
- Manages include/exclude patterns
- Applies filters to files
- Supports glob patterns
- Filters hidden/system files

#### 6. Progress Tracker (progress_tracker.py)
- Tracks scan progress
- Invokes progress callbacks
- Reports file counts, bytes scanned
- Handles cancellation signals

#### 7. Scan State (scan_state.py)
- Saves scan state for resume
- Loads scan state from disk
- Tracks completed files
- Manages checkpoint system

#### 8. Worker Pool (worker_pool.py)
- Manages parallel worker threads
- Distributes work to workers
- Handles worker errors
- Manages thread lifecycle

---

## Threading Model

### Architecture

```
Main Thread
    ↓
Scanner (orchestrator)
    ↓
Worker Pool (thread pool)
    ↓
Worker Threads (N workers)
    ↓
File Scanner (per file)
    ↓
Hash Generator (streaming)
```

### Thread Pool Design

**Configuration:**
- Default workers: 4 (CPU count * 2 for I/O-bound work)
- Configurable via settings
- Min workers: 2
- Max workers: 16

**Worker Lifecycle:**
1. Worker created from pool
2. Worker receives file path from queue
3. Worker scans file (metadata + hash)
4. Worker returns result to main thread
5. Worker waits for next file
6. Pool shutdown when scan complete or cancelled

**Thread Safety:**
- Queue for work distribution (thread-safe)
- Progress tracker with atomic operations
- Cancellation flag (thread-safe)
- Scan state with file locking

### Cancellation

**Mechanism:**
- Atomic cancellation flag
- Checked at strategic points:
  - Before each file scan
  - During hash generation (chunk boundaries)
  - After worker pool iteration

**Graceful Shutdown:**
- Workers finish current file
- Worker pool shutdown
- Scan state saved
- Progress callback notified

---

## Complexity Analysis

### Time Complexity

**Directory Traversal:**
- O(N) where N = number of files
- Each file visited once
- Parallel: O(N / W) where W = workers

**Hash Generation:**
- O(F) where F = file size
- Streaming: O(F / C) where C = chunk size
- Parallel: O(ΣF / W) across workers

**Duplicate Detection:**
- O(N) for hash lookup (hash table)
- O(1) per file lookup

**Overall:**
- Sequential: O(N + ΣF)
- Parallel: O(N / W + ΣF / W)

### Space Complexity

**In-Memory:**
- File queue: O(Q) where Q = queue size (configurable, default 1000)
- Worker pool: O(W) where W = workers
- Duplicate map: O(D) where D = unique hashes
- Scan state: O(S) where S = state size on disk

**Disk:**
- Scan state: O(N) (one entry per file)
- No in-memory storage of all files

**Overall:**
- In-memory: O(Q + W + D)
- Disk: O(N)

---

## Performance Analysis

### Bottlenecks

**1. I/O Bound Operations:**
- Directory traversal (stat calls)
- File reading (hash generation)
- Write scan state

**Mitigation:**
- Parallel processing with worker pool
- Async I/O where possible
- Batch write operations

**2. CPU Bound Operations:**
- SHA-256 computation
- Path normalization
- Filter matching

**Mitigation:**
- Worker pool distributes CPU work
- Streaming reduces memory pressure
- Optimized filter matching

**3. Synchronization:**
- Progress updates
- Scan state writes
- Duplicate map updates

**Mitigation:**
- Atomic operations
- Batch updates
- Lock-free data structures where possible

### Optimization Strategies

**1. Directory Traversal:**
- Use `os.scandir()` instead of `os.listdir()` (faster)
- Batch directory reads
- Skip unnecessary stat calls

**2. Hash Generation:**
- Optimal chunk size: 64KB (tunable)
- Memory-mapped files for large files
- Early termination on cancellation

**3. Duplicate Detection:**
- Hash table (dict) for O(1) lookup
- Bloom filter for approximate detection (optional)
- Periodic checkpoint to disk

**4. Progress Tracking:**
- Throttle progress callbacks (e.g., every 100 files)
- Batch updates to reduce overhead
- Optional progress for large scans

---

## Extension Points

### 1. Custom Hash Algorithms

**Interface:**
```python
class HashAlgorithm(ABC):
    @abstractmethod
    def compute(self, file_path: str) -> str:
        pass
```

**Implementations:**
- SHA-256 (default)
- MD5 (legacy support)
- BLAKE2 (faster alternative)

### 2. Custom Filters

**Interface:**
```python
class FileFilter(ABC):
    @abstractmethod
    def should_include(self, file_path: str) -> bool:
        pass
```

**Implementations:**
- Extension filter
- Size filter
- Age filter
- Content filter (hash-based)

### 3. Custom Progress Callbacks

**Interface:**
```python
class ProgressCallback(ABC):
    @abstractmethod
    def on_progress(self, progress: ScanProgress):
        pass

    @abstractmethod
    def on_complete(self, result: ScanResult):
        pass

    @abstractmethod
    def on_error(self, error: ScanError):
        pass
```

**Implementations:**
- Console progress bar
- GUI progress indicator
- Remote progress (WebSocket)
- Log file progress

### 4. Custom Scan State Storage

**Interface:**
```python
class StateStorage(ABC):
    @abstractmethod
    def save(self, state: ScanState):
        pass

    @abstractmethod
    def load(self) -> ScanState:
        pass
```

**Implementations:**
- JSON file (default)
- SQLite database
- Redis (distributed)
- Cloud storage

### 5. Custom Worker Pool

**Interface:**
```python
class WorkerPool(ABC):
    @abstractmethod
    def submit(self, task: Callable):
        pass

    @abstractmethod
    def shutdown(self):
        pass
```

**Implementations:**
- ThreadPoolExecutor (default)
- ProcessPoolExecutor (CPU-bound)
- AsyncIO (async)
- Distributed (Celery)

---

## Data Structures

### File Info

```python
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
```

### Scan Progress

```python
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
```

### Scan Result

```python
@dataclass
class ScanResult:
    """Result of a scan operation."""
    files: List[FileInfo]
    duplicates: Dict[str, List[FileInfo]]
    errors: List[ScanError]
    duration: float
    cancelled: bool
```

### Scan State

```python
@dataclass
class ScanState:
    """State for resuming interrupted scans."""
    scan_id: str
    root_path: str
    completed_files: Set[str]
    last_checkpoint: datetime
    configuration: ScanConfiguration
```

---

## Error Handling

### Error Types

**1. Permission Errors:**
- Skip file, log warning
- Continue scan
- Track in errors list

**2. Access Errors:**
- Skip file, log warning
- Continue scan
- Track in errors list

**3. Symbolic Link Errors:**
- Detect loops, skip
- Log warning
- Continue scan

**4. Cancellation Errors:**
- Graceful shutdown
- Save scan state
- Notify progress callback

**5. System Errors:**
- Critical, abort scan
- Log error
- Notify progress callback

### Error Recovery

**Retry Strategy:**
- No retries for file access errors (likely persistent)
- Retry for transient errors (network, temporary locks)
- Max retries: 3
- Exponential backoff

**Error Isolation:**
- One file error doesn't stop scan
- Worker errors don't stop other workers
- Critical errors abort entire scan

---

## Logging

### Log Levels

**DEBUG:**
- Detailed progress (every file)
- Worker pool status
- State checkpoint details

**INFO:**
- Scan start/stop
- Progress updates (throttled)
- Summary statistics

**WARNING:**
- Skipped files (permissions, filters)
- Symbolic link loops
- Duplicate detection

**ERROR:**
- File access errors
- Worker errors
- Critical system errors

### Structured Logging

**Fields:**
- `scan_id`: Unique scan identifier
- `file_path`: File being processed
- `file_size`: File size
- `hash`: File hash (DEBUG only)
- `worker_id`: Worker thread ID
- `duration`: Operation duration
- `error`: Error details (if applicable)

---

## Configuration

### Scan Configuration

```python
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
```

---

## Testing Strategy

### Unit Tests

**Test Coverage:**
- Path resolution (symbolic links, normalization)
- Hash generation (streaming, cancellation)
- Filter manager (include/exclude patterns)
- Progress tracker (callbacks, throttling)
- Scan state (save/load, resume)
- Worker pool (task distribution, shutdown)
- Scanner (integration, cancellation, resume)

**Test Data:**
- Small file set (100 files)
- Medium file set (1,000 files)
- Large file set (10,000 files)
- Symbolic links
- Hidden files
- Duplicate files

### Integration Tests

**Test Scenarios:**
- Full scan with all features
- Cancellation during scan
- Resume interrupted scan
- Parallel processing
- Memory efficiency

### Benchmark Tests

**Metrics:**
- Files per second
- Peak memory usage
- CPU utilization
- I/O operations
- Hash computation rate

**Test Sizes:**
- 1,000 files
- 10,000 files
- 100,000 files (if feasible)

---

## Security Considerations

### Path Traversal

**Validation:**
- Resolve paths to absolute
- Detect and reject parent directory references
- Detect symbolic link loops
- Validate against root path

### Resource Limits

**Protection:**
- Max file size (configurable)
- Max recursion depth (configurable)
- Max scan duration (configurable)
- Memory limits (monitor and abort)

### Information Disclosure

**Logging:**
- Don't log file contents
- Don't log sensitive paths (configurable)
- Hash only (DEBUG level)

---

## Performance Targets

### Benchmarks

**Target for 10,000 files:**
- Files/sec: 500-1000
- Peak memory: < 500MB
- CPU utilization: 60-80%
- Duration: 10-20 seconds

**Scaling:**
- Linear scaling with workers (up to CPU count)
- Constant memory (independent of file count)
- Sub-linear I/O (parallel)

---

## Dependencies

### Required

- `pathlib` - Path manipulation
- `hashlib` - SHA-256 hashing
- `os` - File system operations
- `threading` - Worker pool
- `queue` - Work queue
- `logging` - Structured logging
- `dataclasses` - Data structures
- `typing` - Type hints
- `datetime` - Timestamps
- `mimetypes` - MIME type detection

### Optional

- `tqdm` - Progress bar (for CLI)
- `psutil` - System monitoring (for benchmarks)

---

## Future Enhancements

### Short Term

1. **Optimized Hash Generation:**
   - Memory-mapped files
   - SIMD instructions (if available)
   - GPU acceleration (optional)

2. **Intelligent Filtering:**
   - Content-based filtering (hash prefix)
   - Machine learning (spam detection)
   - Heuristic filters

### Long Term

1. **Distributed Scanning:**
   - Worker nodes
   - Task distribution
   - Result aggregation

2. **Real-time Monitoring:**
   - Inotify integration
   - Continuous scanning
   - Event-driven updates

3. **Cloud Storage:**
   - S3 scanner
   - Azure Blob scanner
   - Google Cloud Storage scanner

---

## Summary

The Scanner module is designed for high-performance file discovery with:
- Parallel processing for scalability
- Streaming hash generation for memory efficiency
- Cancellation and resume for robustness
- Extension points for flexibility
- Comprehensive testing for reliability

**Status:** Design complete, ready for implementation

---

**Document Version:** 1.0
**Last Updated:** 2024-01-01
**Next Review:** After implementation and benchmarks
