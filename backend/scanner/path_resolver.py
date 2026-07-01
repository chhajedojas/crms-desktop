"""
Path resolver for resolving and validating file paths.

This module handles path resolution, normalization, and validation
to prevent path traversal attacks and detect symbolic link loops.
"""

from pathlib import Path
from typing import Set
from core import get_logger


class PathResolutionError(Exception):
    """Exception raised when path resolution fails."""

    pass


class PathResolver:
    """Resolves and validates file paths."""

    def __init__(self, root_path: Path):
        """
        Initialize path resolver.

        Args:
            root_path: Root path for resolution
        """
        self.root_path = root_path.resolve()
        self.logger = get_logger(__name__)
        self._visited_symlinks: Set[Path] = set()

    def resolve_path(self, path: Path) -> Path:
        """
        Resolve a path relative to root.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute path

        Raises:
            PathResolutionError: If path is invalid
        """
        try:
            # Resolve to absolute path
            resolved = path.resolve()

            # Check if path is within root
            try:
                resolved.relative_to(self.root_path)
            except ValueError:
                raise PathResolutionError(f"Path {resolved} is outside root {self.root_path}")

            # Check for parent directory references
            if ".." in str(resolved):
                raise PathResolutionError(f"Path {resolved} contains parent directory references")

            return resolved

        except PathResolutionError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error resolving path {path}: {str(e)}")
            raise PathResolutionError(f"Failed to resolve path: {str(e)}")

    def is_within_root(self, path: Path) -> bool:
        """
        Check if path is within root.

        Args:
            path: Path to check

        Returns:
            True if path is within root, False otherwise
        """
        try:
            resolved = path.resolve()
            resolved.relative_to(self.root_path)
            return True
        except ValueError:
            return False

    def is_symlink_loop(self, path: Path) -> bool:
        """
        Check if path is part of a symbolic link loop.

        Args:
            path: Path to check

        Returns:
            True if path is part of a loop, False otherwise
        """
        try:
            if not path.is_symlink():
                return False

            resolved = path.resolve()

            if resolved in self._visited_symlinks:
                self.logger.warning(f"Symbolic link loop detected: {path} -> {resolved}")
                return True

            self._visited_symlinks.add(resolved)
            return False

        except Exception as e:
            self.logger.error(f"Error checking symlink loop for {path}: {str(e)}")
            return True  # Assume loop on error

    def clear_symlink_cache(self):
        """Clear the visited symlinks cache."""
        self._visited_symlinks.clear()

    def get_relative_path(self, path: Path) -> Path:
        """
        Get relative path from root.

        Args:
            path: Path to convert

        Returns:
            Relative path from root

        Raises:
            PathResolutionError: If path is not within root
        """
        try:
            resolved = path.resolve()
            return resolved.relative_to(self.root_path)
        except ValueError:
            raise PathResolutionError(f"Path {resolved} is not within root {self.root_path}")
