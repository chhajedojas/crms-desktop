"""
Unit tests for filter manager.
"""

import pytest
import tempfile
from pathlib import Path
from scanner.filter_manager import FilterManager


class TestFilterManager:
    """Tests for FilterManager class."""

    def test_init_default(self):
        """Test initialization with defaults."""
        manager = FilterManager()
        assert manager.include_patterns == []
        assert manager.exclude_patterns == []
        assert not manager.include_hidden
        assert not manager.include_system

    def test_init_with_patterns(self):
        """Test initialization with patterns."""
        manager = FilterManager(
            include_patterns=["*.txt"],
            exclude_patterns=["*.tmp"],
            include_hidden=True,
            include_system=True,
        )
        assert "*.txt" in manager.include_patterns
        assert "*.tmp" in manager.exclude_patterns
        assert manager.include_hidden
        assert manager.include_system

    def test_should_include_default(self):
        """Test should_include with default filters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager()
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            assert manager.should_include(test_file)

    def test_should_include_with_include_pattern(self):
        """Test should_include with include pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager(include_patterns=["*.txt"])
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            assert manager.should_include(test_file)

    def test_should_include_exclude_pattern(self):
        """Test should_include with exclude pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager(exclude_patterns=["*.tmp"])
            test_file = Path(tmpdir) / "test.tmp"
            test_file.touch()
            assert not manager.should_include(test_file)

    def test_should_include_hidden_file(self):
        """Test should_include excludes hidden files by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager()
            test_file = Path(tmpdir) / ".hidden"
            test_file.touch()
            assert not manager.should_include(test_file)

    def test_should_include_hidden_file_allowed(self):
        """Test should_include includes hidden files when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager(include_hidden=True)
            test_file = Path(tmpdir) / ".hidden"
            test_file.touch()
            assert manager.should_include(test_file)

    def test_should_include_system_file(self):
        """Test should_include excludes system files by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager()
            test_file = Path(tmpdir) / "Thumbs.db"
            test_file.touch()
            assert not manager.should_include(test_file)

    def test_should_include_system_file_allowed(self):
        """Test should_include includes system files when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager(include_system=True)
            test_file = Path(tmpdir) / "Thumbs.db"
            test_file.touch()
            assert manager.should_include(test_file)

    def test_should_include_no_match_include_pattern(self):
        """Test should_include excludes when no include pattern matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FilterManager(include_patterns=["*.txt"])
            test_file = Path(tmpdir) / "test.pdf"
            test_file.touch()
            assert not manager.should_include(test_file)
