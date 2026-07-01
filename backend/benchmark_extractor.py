"""
Benchmark script for metadata extractors.

This script benchmarks extraction performance for PDF, Excel, and Word files.
"""

import time
import tempfile
from pathlib import Path
from extractor.factory import ExtractorFactory
from extractor.data_structures import ExtractionStatus


def benchmark_pdf(count=100):
    """Benchmark PDF extraction."""
    print(f"\n=== Benchmarking {count} PDFs ===")

    # Create sample PDFs (placeholder - would need real PDF library)
    factory = ExtractorFactory()

    # Placeholder: Create text files instead of PDFs for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        files = []

        for i in range(count):
            test_file = tmpdir_path / f"test_{i}.txt"
            test_file.write_text(f"Test content {i}")
            files.append(test_file)

        start = time.time()
        success = 0
        failed = 0
        total_time = 0

        for file_path in files:
            try:
                # Note: These are .txt files, not PDFs
                # This is a placeholder for actual PDF benchmarking
                result = factory.extract(file_path)
                total_time += result.extraction_time
                if result.status == ExtractionStatus.SUCCESS:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1

        duration = time.time() - start

        print(f"Total duration: {duration:.2f}s")
        print(f"Average per file: {duration / count:.4f}s")
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        print(f"Files/sec: {count / duration:.2f}")


def benchmark_excel(count=100):
    """Benchmark Excel extraction."""
    print(f"\n=== Benchmarking {count} Excel files ===")

    factory = ExtractorFactory()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        files = []

        for i in range(count):
            test_file = tmpdir_path / f"test_{i}.xlsx"
            # Placeholder: create empty files
            test_file.write_bytes(b"")
            files.append(test_file)

        start = time.time()
        success = 0
        failed = 0

        for file_path in files:
            try:
                result = factory.extract(file_path)
                if result.status == ExtractionStatus.SUCCESS:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1

        duration = time.time() - start

        print(f"Total duration: {duration:.2f}s")
        print(f"Average per file: {duration / count:.4f}s")
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        print(f"Files/sec: {count / duration:.2f}")


def benchmark_word(count=100):
    """Benchmark Word extraction."""
    print(f"\n=== Benchmarking {count} Word files ===")

    factory = ExtractorFactory()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        files = []

        for i in range(count):
            test_file = tmpdir_path / f"test_{i}.docx"
            # Placeholder: create empty files
            test_file.write_bytes(b"")
            files.append(test_file)

        start = time.time()
        success = 0
        failed = 0

        for file_path in files:
            try:
                result = factory.extract(file_path)
                if result.status == ExtractionStatus.SUCCESS:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1

        duration = time.time() - start

        print(f"Total duration: {duration:.2f}s")
        print(f"Average per file: {duration / count:.4f}s")
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        print(f"Files/sec: {count / duration:.2f}")


if __name__ == "__main__":
    print("Metadata Extraction Benchmarks")
    print("================================")
    print("Note: These are placeholder benchmarks using empty files.")
    print("Actual benchmarks require real sample documents.")

    benchmark_pdf(100)
    benchmark_excel(100)
    benchmark_word(100)

    print("\n=== Benchmark Complete ===")
    print("Note: Replace placeholder files with real documents for accurate benchmarks.")
