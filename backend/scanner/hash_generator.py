"""
Hash generator for computing SHA-256 hashes using streaming.

This module provides streaming hash generation to avoid loading
entire files into memory, making it suitable for large files.
"""

import hashlib
from pathlib import Path
from typing import Optional, Callable
from core import get_logger


class HashGenerationError(Exception):
    """Exception raised when hash generation fails."""

    pass


class HashGenerator:
    """Generates SHA-256 hashes using streaming."""

    def __init__(self, chunk_size: int = 65536):
        """
        Initialize hash generator.

        Args:
            chunk_size: Size of chunks to read (default 64KB)
        """
        self.chunk_size = chunk_size
        self.logger = get_logger(__name__)

    def compute_hash(
        self,
        file_path: Path,
        cancellation_flag: Optional[Callable[[], bool]] = None,
    ) -> str:
        """
        Compute SHA-256 hash of a file using streaming.

        Args:
            file_path: Path to file
            cancellation_flag: Optional callable that returns True if cancelled

        Returns:
            SHA-256 hash as hexadecimal string

        Raises:
            HashGenerationError: If hash generation fails
        """
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while True:
                    # Check for cancellation
                    if cancellation_flag and cancellation_flag():
                        self.logger.debug(f"Hash generation cancelled for {file_path}")
                        raise HashGenerationError("Hash generation cancelled")

                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    sha256_hash.update(chunk)

            hash_hex = sha256_hash.hexdigest()
            self.logger.debug(f"Computed hash for {file_path}: {hash_hex}")
            return hash_hex

        except IOError as e:
            self.logger.error(f"IO error reading {file_path}: {str(e)}")
            raise HashGenerationError(f"Failed to read file: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error computing hash for {file_path}: {str(e)}")
            raise HashGenerationError(f"Failed to compute hash: {str(e)}")

    def compute_hash_string(self, data: str) -> str:
        """
        Compute SHA-256 hash of a string.

        Args:
            data: String to hash

        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data.encode("utf-8"))
        return sha256_hash.hexdigest()
