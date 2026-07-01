"""
Unit tests for hash generator.
"""

import pytest
import tempfile
from pathlib import Path
from scanner.hash_generator import HashGenerator, HashGenerationError


class TestHashGenerator:
    """Tests for HashGenerator class."""

    def test_init_default_chunk_size(self):
        """Test initialization with default chunk size."""
        generator = HashGenerator()
        assert generator.chunk_size == 65536

    def test_init_custom_chunk_size(self):
        """Test initialization with custom chunk size."""
        generator = HashGenerator(chunk_size=1024)
        assert generator.chunk_size == 1024

    def test_compute_hash_small_file(self):
        """Test hash computation for small file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            generator = HashGenerator()
            hash_value = generator.compute_hash(temp_path)
            assert hash_value
            assert len(hash_value) == 64  # SHA-256 hex length
        finally:
            temp_path.unlink()

    def test_compute_hash_empty_file(self):
        """Test hash computation for empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = Path(f.name)

        try:
            generator = HashGenerator()
            hash_value = generator.compute_hash(temp_path)
            assert hash_value
            assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        finally:
            temp_path.unlink()

    def test_compute_hash_large_file(self):
        """Test hash computation for large file (streaming)."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Write 1MB of data
            f.write(b"x" * 1024 * 1024)
            temp_path = Path(f.name)

        try:
            generator = HashGenerator()
            hash_value = generator.compute_hash(temp_path)
            assert hash_value
            assert len(hash_value) == 64
        finally:
            temp_path.unlink()

    def test_compute_hash_with_cancellation(self):
        """Test hash computation with cancellation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            generator = HashGenerator()
            cancellation_flag = lambda: True
            with pytest.raises(HashGenerationError):
                generator.compute_hash(temp_path, cancellation_flag)
        finally:
            temp_path.unlink()

    def test_compute_hash_nonexistent_file(self):
        """Test hash computation for nonexistent file."""
        generator = HashGenerator()
        with pytest.raises(HashGenerationError):
            generator.compute_hash(Path("/nonexistent/file.txt"))

    def test_compute_hash_string(self):
        """Test hash computation for string."""
        generator = HashGenerator()
        hash_value = generator.compute_hash_string("test")
        assert hash_value
        assert len(hash_value) == 64
