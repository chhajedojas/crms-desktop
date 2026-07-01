"""
Tests for core configuration module.
"""

import pytest

from core import Settings, get_settings


def test_settings_creation():
    """Test that settings can be created."""
    settings = Settings()
    assert settings is not None
    assert settings.app_name == "CRMS"
    assert settings.app_version == "1.0.0"


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_database_config():
    """Test database configuration."""
    settings = Settings()
    assert settings.database.database_path is not None
    assert settings.database.duckdb_path is not None


def test_ipc_config():
    """Test IPC configuration."""
    settings = Settings()
    assert settings.ipc.ipc_mode in ["stdio", "socket", "named_pipe"]
    assert 1 <= settings.ipc.ipc_port <= 65535


def test_invalid_ipc_mode():
    """Test that invalid IPC mode raises error."""
    with pytest.raises(ValueError):
        from core import IPCConfig

        IPCConfig(ipc_mode="invalid_mode")


def test_invalid_port():
    """Test that invalid port raises error."""
    with pytest.raises(ValueError):
        from core import IPCConfig

        IPCConfig(ipc_port=70000)


def test_classification_confidence_threshold():
    """Test classification confidence threshold validation."""
    from core import ClassificationConfig

    # Valid threshold
    config = ClassificationConfig(classification_confidence_threshold=0.8)
    assert config.classification_confidence_threshold == 0.8

    # Invalid threshold
    with pytest.raises(ValueError):
        ClassificationConfig(classification_confidence_threshold=1.5)


def test_financial_year_start_format():
    """Test financial year start format validation."""
    from core import ReorganizationConfig

    # Valid format
    config = ReorganizationConfig(financial_year_start="04-01")
    assert config.financial_year_start == "04-01"

    # Invalid format
    with pytest.raises(ValueError):
        ReorganizationConfig(financial_year_start="invalid")
