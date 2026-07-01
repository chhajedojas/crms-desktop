"""
File scanner for scanning individual files and collecting metadata.
"""

import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from scanner.data_structures import FileInfo
from scanner.hash_generator import HashGenerator, HashGenerationError
from core import get_logger


class FileScanner:
    """Scans individual files and collects metadata."""

    def __init__(
        self,
        root_path: Path,
        enable_hash: bool = True,
        chunk_size: int = 65536,
    ):
        """
        Initialize file scanner.

        Args:
            root_path: Root path for relative path calculation
            enable_hash: Whether to compute file hashes
            chunk_size: Chunk size for hash generation
        """
        self.root_path = root_path
        self.enable_hash = enable_hash
        self.chunk_size = chunk_size
        self.hash_generator = HashGenerator(chunk_size) if enable_hash else None
        self.logger = get_logger(__name__)

    def scan_file(
        self,
        file_path: Path,
        cancellation_flag: Optional[Callable[[], bool]] = None,
    ) -> FileInfo:
        """
        Scan a single file and collect metadata.

        Args:
            file_path: Path to file
            cancellation_flag: Optional callable that returns True if cancelled

        Returns:
            FileInfo object with metadata

        Raises:
            IOError: If file cannot be accessed
        """
        try:
            # Check for cancellation
            if cancellation_flag and cancellation_flag():
                raise IOError("Scan cancelled")

            # Get file stats
            stat = file_path.stat()

            # Compute hash if enabled
            file_hash = None
            if self.enable_hash and self.hash_generator:
                file_hash = self.hash_generator.compute_hash(file_path, cancellation_flag)

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            mime_type = mime_type or "application/octet-stream"

            # Create file info
            file_info = FileInfo(
                absolute_path=str(file_path.resolve()),
                relative_path=str(file_path.relative_to(self.root_path)),
                filename=file_path.name,
                extension=file_path.suffix or "",
                mime_type=mime_type,
                size=stat.st_size,
                created_time=datetime.fromtimestamp(stat.st_ctime),
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                permissions=stat.st_mode,
                hash=file_hash,
            )

            self.logger.debug(f"Scanned file: {file_path}")
            return file_info

        except IOError as e:
            self.logger.error(f"IO error scanning {file_path}: {str(e)}")
            raise
        except HashGenerationError as e:
            self.logger.error(f"Hash generation error for {file_path}: {str(e)}")
            raise IOError(f"Hash generation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error scanning {file_path}: {str(e)}")
            raise IOError(f"Failed to scan file: {str(e)}")
