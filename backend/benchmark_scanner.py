"""
Benchmark script for scanner performance testing.
"""

import time
import tempfile
import os
from pathlib import Path
from scanner import Scanner, ScanConfiguration
from scanner.data_structures import ScanProgress


def create_synthetic_files(root_path: Path, count: int, size_kb: int = 1):
    """Create synthetic files for benchmarking.

    Args:
        root_path: Root directory for files
        count: Number of files to create
        size_kb: Size of each file in KB
    """
    data = b"x" * (size_kb * 1024)
    for i in range(count):
        file_path = root_path / f"file_{i:06d}.txt"
        file_path.write_bytes(data)


def benchmark_scanner(file_count: int, file_size_kb: int = 1, max_workers: int = 4):
    """Benchmark scanner performance.

    Args:
        file_count: Number of files to scan
        file_size_kb: Size of each file in KB
        max_workers: Number of worker threads

    Returns:
        Dictionary with benchmark results
    """
    print(f"\n=== Benchmark: {file_count} files ({file_size_kb}KB each, {max_workers} workers) ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        print(f"Creating {file_count} synthetic files...")
        create_synthetic_files(root, file_count, file_size_kb)
        print(f"Files created.")

        config = ScanConfiguration(
            root_path=str(root),
            enable_hash=True,
            enable_duplicate_detection=True,
            max_workers=max_workers,
        )

        scanner = Scanner(config)

        # Track progress
        def progress_callback(progress: ScanProgress):
            if progress.scanned_files % 1000 == 0 or progress.scanned_files == progress.total_files:
                print(f"Progress: {progress.scanned_files}/{progress.total_files} files ({progress.percentage:.1f}%)")

        print("Starting scan...")
        start_time = time.time()
        result = scanner.scan(progress_callback=progress_callback)
        end_time = time.time()

        duration = end_time - start_time
        files_per_sec = file_count / duration if duration > 0 else 0
        total_bytes = file_count * file_size_kb * 1024
        bytes_per_sec = total_bytes / duration if duration > 0 else 0

        results = {
            "file_count": file_count,
            "file_size_kb": file_size_kb,
            "max_workers": max_workers,
            "duration": duration,
            "files_per_sec": files_per_sec,
            "bytes_per_sec": bytes_per_sec,
            "total_bytes": total_bytes,
            "files_scanned": len(result.files),
            "errors": len(result.errors),
            "duplicates": len(result.duplicates),
        }

        print(f"\nResults:")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Files/sec: {files_per_sec:.2f}")
        print(f"  Throughput: {bytes_per_sec / 1024 / 1024:.2f} MB/s")
        print(f"  Files scanned: {len(result.files)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Duplicates: {len(result.duplicates)}")

        return results


if __name__ == "__main__":
    print("Scanner Performance Benchmark")
    print("=" * 50)

    # Test with different file counts
    test_configs = [
        (1000, 1, 4),
        (10000, 1, 4),
        (50000, 1, 4),
    ]

    all_results = []
    for file_count, file_size_kb, max_workers in test_configs:
        try:
            results = benchmark_scanner(file_count, file_size_kb, max_workers)
            all_results.append(results)
        except Exception as e:
            print(f"Error in benchmark: {e}")

    print("\n" + "=" * 50)
    print("Benchmark Summary")
    print("=" * 50)
    for results in all_results:
        print(f"\n{results['file_count']} files:")
        print(f"  {results['files_per_sec']:.2f} files/sec")
        print(f"  {results['bytes_per_sec'] / 1024 / 1024:.2f} MB/s")
