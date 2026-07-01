"""
Filter manager for applying include/exclude filters to files.

This module manages include and exclude patterns using glob patterns
and filters hidden/system files.
"""

import os
from pathlib import Path
from typing import List, Optional
from fnmatch import fnmatch
from core import get_logger


class FilterManager:
    """Manages include/exclude filters for file scanning."""

    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        include_hidden: bool = False,
        include_system: bool = False,
    ):
        """
        Initialize filter manager.

        Args:
            include_patterns: Glob patterns to include (empty = all)
            exclude_patterns: Glob patterns to exclude
            include_hidden: Whether to include hidden files
            include_system: Whether to include system files
        """
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.include_hidden = include_hidden
        self.include_system = include_system
        self.logger = get_logger(__name__)

    def should_include(self, file_path: Path) -> bool:
        """
        Determine if a file should be included based on filters.

        Args:
            file_path: Path to file

        Returns:
            True if file should be included, False otherwise
        """
        # Check hidden files
        if not self.include_hidden and self._is_hidden(file_path):
            self.logger.debug(f"Excluding hidden file: {file_path}")
            return False

        # Check system files
        if not self.include_system and self._is_system(file_path):
            self.logger.debug(f"Excluding system file: {file_path}")
            return False

        # Check exclude patterns
        if self._matches_patterns(file_path, self.exclude_patterns):
            self.logger.debug(f"Excluding by pattern: {file_path}")
            return False

        # Check include patterns
        if self.include_patterns:
            if not self._matches_patterns(file_path, self.include_patterns):
                self.logger.debug(f"Not matching include pattern: {file_path}")
                return False

        return True

    def _is_hidden(self, file_path: Path) -> bool:
        """
        Check if file is hidden.

        Args:
            file_path: Path to file

        Returns:
            True if file is hidden, False otherwise
        """
        # Unix/Linux: starts with .
        if file_path.name.startswith("."):
            return True

        # Windows: check hidden attribute
        if os.name == "nt":
            try:
                import win32api
                import win32con

                attribute = win32api.GetFileAttributes(str(file_path))
                if attribute & win32con.FILE_ATTRIBUTE_HIDDEN:
                    return True
            except (ImportError, AttributeError):
                # win32api not available, skip check
                pass

        return False

    def _is_system(self, file_path: Path) -> bool:
        """
        Check if file is a system file.

        Args:
            file_path: Path to file

        Returns:
            True if file is system, False otherwise
        """
        # Common system directories/files
        system_names = {
            "System Volume Information",
            "$RECYCLE.BIN",
            "Thumbs.db",
            "desktop.ini",
            ".DS_Store",
            ".git",
            ".svn",
            ".hg",
        }

        # Check if any parent directory is system
        for parent in file_path.parents:
            if parent.name in system_names:
                return True

        # Check if file itself is system
        if file_path.name in system_names:
            return True

        # Windows: check system attribute
        if os.name == "nt":
            try:
                import win32api
                import win32con

                attribute = win32api.GetFileAttributes(str(file_path))
                if attribute & win32con.FILE_ATTRIBUTE_SYSTEM:
                    return True
            except (ImportError, AttributeError):
                # win32api not available, skip check
                pass

        return False

    def _matches_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """
        Check if file path matches any of the patterns.

        Args:
            file_path: Path to file
            patterns: List of glob patterns

        Returns:
            True if matches any pattern, False otherwise
        """
        file_str = str(file_path)

        for pattern in patterns:
            if fnmatch(file_str, pattern):
                return True

            # Also check filename
            if fnmatch(file_path.name, pattern):
                return True

        return False
