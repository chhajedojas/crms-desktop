"""
Base extractor module for CRMS backend.
Provides base extractor interface and utilities.
"""

from typing import Any, Dict

from core import BaseExtractor


class BaseDocumentExtractor(BaseExtractor):
    """Base class for document extractors."""

    def can_extract(self, file_path: str) -> bool:
        """Check if this extractor can handle the given file."""
        # Placeholder implementation
        return False

    def extract(self, file_path: str) -> Dict[str, Any]:
        """Extract data from the given file."""
        # Placeholder implementation
        return {}
