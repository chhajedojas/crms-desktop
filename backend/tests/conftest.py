"""
Pytest configuration for CRMS backend tests.
Provides fixtures and test configuration.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_document():
    """Fixture providing sample document data."""
    return {
        "file_path": "/path/to/document.pdf",
        "file_name": "document.pdf",
        "file_size": 1024,
        "file_type": "pdf",
    }


@pytest.fixture
def sample_metadata():
    """Fixture providing sample metadata."""
    return {
        "customer": "Test Customer",
        "vendor": "Test Vendor",
        "invoice_number": "INV-001",
        "gstin": "27AAPFU0939F1ZV",
        "date": "2024-01-01",
        "amount": 1000.00,
    }
