"""
Base classifier module for CRMS backend.
Provides base classifier interface and utilities.
"""

from typing import Any, Dict, Tuple

from core import BaseClassifier


class BaseDocumentClassifier(BaseClassifier):
    """Base class for document classifiers."""

    def classify(self, content: str, metadata: Dict[str, Any]) -> Tuple[str, float]:
        """Classify document and return (type, confidence)."""
        # Placeholder implementation
        return ("Unknown", 0.0)
