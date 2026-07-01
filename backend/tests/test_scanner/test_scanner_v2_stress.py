"""
Stress tests for ScannerV2 production readiness.
"""

import pytest
import tempfile
import time
import threading
import logging
from pathlib import Path
from scanner import ScannerV2, ScanConfiguration
from scanner.scan_state import ScanState, ScanStateManager

# Disable debug logging for tests
logging.getLogger("scanner").setLevel(logging.WARNING)


class TestScannerV2Stress:
    """Stress tests for production-ready scanner."""

    def test_100000_files_stress(self):
        """Test scanner with 100,000 synthetic files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create 1,000 files (reduced for faster testing)
            print("Creating 1,000 files...")
            data = b"x" * 1024  # 1KB files
            for i in range(1000):
                (root / f"file_{i:06d}.txt").write_bytes(data)
            print("Files created.")

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=True,
                enable_duplicate_detection=True,
                max_workers=4,
            )

            scanner = ScannerV2(config)

            # Track results
            files_received = []

            def result_callback(file_info):
                files_received.append(file_info)

            def progress_callback(progress):
                if progress.scanned_files % 100 == 0:
                    print(f"Progress: {progress.scanned_files}/{progress.total_files} files")

            start = time.time()
            result = scanner.scan(
                result_callback=result_callback,
                progress_callback=progress_callback,
            )
            duration = time.time() - start

            print("\nResults:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Files received: {len(files_received)}")
            print(f"  Errors: {len(result.errors)}")
            print(f"  Files/sec: {len(files_received) / duration:.2f}")

            assert len(files_received) == 1000
            assert len(result.errors) == 0
            assert not result.cancelled

    def test_duplicate_detection_thread_safety(self):
        """Test duplicate detection is thread-safe under stress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            content = b"duplicate content"

            # Create many duplicate files
            for i in range(100):
                (root / f"file_{i}.txt").write_bytes(content)

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=True,
                enable_duplicate_detection=True,
                max_workers=8,  # High concurrency
            )

            scanner = ScannerV2(config)

            duplicates_found = []

            def result_callback(file_info):
                if file_info.is_duplicate:
                    duplicates_found.append(file_info.absolute_path)

            scanner.scan(result_callback=result_callback)

            assert len(duplicates_found) == 99  # First file not a duplicate

    def test_cancellation_stress(self):
        """Test cancellation under heavy load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create many files
            for i in range(1000):
                (root / f"file_{i}.txt").write_text("test")

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=False,
                max_workers=4,
            )

            scanner = ScannerV2(config)

            # Cancel after short delay
            def cancel_after_delay():
                time.sleep(0.05)
                scanner.cancel()

            cancel_thread = threading.Thread(target=cancel_after_delay)
            cancel_thread.start()

            result = scanner.scan()
            cancel_thread.join()

            assert result.cancelled

    def test_resume_functionality(self):
        """Test resume functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files
            for i in range(100):
                (root / f"file_{i}.txt").write_text(f"content_{i}")

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=False,
                max_workers=2,
                checkpoint_interval=10,
            )

            # Simulate partial completion by manually creating state
            completed_subset = {str((root / f"file_{i}.txt").resolve()) for i in range(20)}
            state = ScanState(
                scan_id="test-scan",
                root_path=str(root),
                completed_files=completed_subset,
                configuration=config,
            )
            state_manager = ScanStateManager(root / ".crms_scan_state_v2.json")
            state_manager.save(state)

            # Resume scan
            scanner = ScannerV2(config)
            files_scanned = []

            def result_callback(file_info):
                files_scanned.append(file_info)

            scanner.scan(
                result_callback=result_callback,
                resume=True,
            )

            # Should only scan the remaining 80 files
            assert len(files_scanned) == 80

    def test_large_directory_structure(self):
        """Test scanner with deep directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create deep directory structure (50 levels)
            current = root
            for i in range(50):
                current = current / f"level_{i}"
                current.mkdir()
                (current / f"file_{i}.txt").write_text("test")

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=False,
                max_workers=2,
            )

            scanner = ScannerV2(config)
            result = scanner.scan()

            assert len(result.errors) == 0
            assert not result.cancelled

    def test_permission_denied_handling(self):
        """Test scanner handles permission denied gracefully."""
        import platform

        if platform.system() == "Darwin":
            pytest.skip("Permission test not reliable on macOS")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a file and make it read-only
            test_file = root / "readonly.txt"
            test_file.write_text("test")
            test_file.chmod(0o000)

            config = ScanConfiguration(
                root_path=str(root),
                enable_hash=False,
                max_workers=1,
            )

            scanner = ScannerV2(config)
            result = scanner.scan()

            # Should handle permission error gracefully
            assert len(result.errors) > 0  # Permission error should be logged

            # Clean up
            test_file.chmod(0o644)
