"""
Unit tests for path resolver.
"""

import pytest
import tempfile
from pathlib import Path
from scanner.path_resolver import PathResolver, PathResolutionError


class TestPathResolver:
    """Tests for PathResolver class."""

    def test_init(self):
        """Test initialization."""
        root = Path("/tmp")
        resolver = PathResolver(root)
        assert resolver.root_path == root.resolve()

    def test_resolve_path_within_root(self):
        """Test resolving path within root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            test_file = root / "test.txt"
            test_file.touch()

            resolved = resolver.resolve_path(test_file)
            assert resolved == test_file.resolve()

    def test_resolve_path_outside_root(self):
        """Test resolving path outside root raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            outside_path = Path("/etc/passwd")
            with pytest.raises(PathResolutionError):
                resolver.resolve_path(outside_path)

    def test_is_within_root_true(self):
        """Test is_within_root returns True for path within root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            test_file = root / "test.txt"
            test_file.touch()

            assert resolver.is_within_root(test_file)

    def test_is_within_root_false(self):
        """Test is_within_root returns False for path outside root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            outside_path = Path("/etc/passwd")
            assert not resolver.is_within_root(outside_path)

    def test_get_relative_path(self):
        """Test getting relative path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            test_file = root / "subdir" / "test.txt"
            test_file.parent.mkdir(parents=True)
            test_file.touch()

            relative = resolver.get_relative_path(test_file)
            assert relative == Path("subdir/test.txt")

    def test_get_relative_path_outside_root(self):
        """Test getting relative path for path outside root raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)

            outside_path = Path("/etc/passwd")
            with pytest.raises(PathResolutionError):
                resolver.get_relative_path(outside_path)

    def test_clear_symlink_cache(self):
        """Test clearing symlink cache."""
        root = Path("/tmp")
        resolver = PathResolver(root)
        resolver._visited_symlinks.add(Path("/some/symlink"))
        resolver.clear_symlink_cache()
        assert len(resolver._visited_symlinks) == 0
