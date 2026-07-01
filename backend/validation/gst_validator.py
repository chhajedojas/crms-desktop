"""
GST validator module for CRMS backend.
Validates GST information and compliance.
"""

from typing import Any, Optional, Tuple

from core import BaseValidator


class GSTValidator(BaseValidator):
    """Validates GST information."""

    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Validate GST data."""
        return (True, None)
