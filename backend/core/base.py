"""
Base classes and interfaces for CRMS backend.
Provides abstract base classes for various components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class BaseResult:
    """Base class for operation results."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseExtractor(ABC):
    """Abstract base class for document extractors."""

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """Check if this extractor can handle the given file."""
        pass

    @abstractmethod
    def extract(self, file_path: str) -> Dict[str, Any]:
        """Extract data from the given file."""
        pass


class BaseClassifier(ABC):
    """Abstract base class for document classifiers."""

    @abstractmethod
    def classify(self, content: str, metadata: Dict[str, Any]) -> Tuple[str, float]:
        """Classify document and return (type, confidence)."""
        pass


class BaseValidator(ABC):
    """Abstract base class for validators."""

    @abstractmethod
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Validate data and return (is_valid, error_message)."""
        pass


class BasePlugin(ABC):
    """Abstract base class for plugins."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Get plugin version."""
        pass


class BaseProcessor(ABC):
    """Abstract base class for pipeline processors."""

    @abstractmethod
    def process(self, data: Any) -> BaseResult:
        """Process data and return result."""
        pass

    @abstractmethod
    def can_process(self, data: Any) -> bool:
        """Check if this processor can handle the data."""
        pass
