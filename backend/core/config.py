"""
Core configuration management for CRMS backend.
Handles environment variables, application settings, and configuration validation.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    database_path: str = Field(default="./data/crms.db", description="Path to SQLite database")
    database_backup_path: str = Field(
        default="./data/backups", description="Path to database backups"
    )
    duckdb_path: str = Field(
        default="./data/crms_analytics.duckdb", description="Path to DuckDB database"
    )

    @field_validator("database_path", "database_backup_path", "duckdb_path")
    @classmethod
    def ensure_path_exists(cls, v: str) -> str:
        """Ensure directory exists for database paths."""
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)


class IPCConfig(BaseSettings):
    """IPC configuration settings for Electron-Python communication."""

    model_config = SettingsConfigDict(env_prefix="IPC_")

    ipc_mode: str = Field(default="stdio", description="IPC mode: stdio, socket, or named_pipe")
    ipc_host: str = Field(default="127.0.0.1", description="IPC host address (socket mode)")
    ipc_port: int = Field(default=8000, description="IPC port number (socket mode)")
    ipc_timeout: int = Field(default=300, description="IPC timeout in seconds")
    ipc_buffer_size: int = Field(default=65536, description="IPC buffer size in bytes")

    @field_validator("ipc_mode")
    @classmethod
    def validate_ipc_mode(cls, v: str) -> str:
        """Validate IPC mode."""
        valid_modes = ["stdio", "socket", "named_pipe"]
        if v.lower() not in valid_modes:
            raise ValueError(f"Invalid IPC mode. Must be one of: {', '.join(valid_modes)}")
        return v.lower()

    @field_validator("ipc_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class OCRConfig(BaseSettings):
    """OCR configuration settings."""

    model_config = SettingsConfigDict(env_prefix="OCR_")

    ocr_enabled: bool = Field(default=True, description="Enable OCR processing")
    ocr_language: str = Field(default="eng", description="OCR language code")
    ocr_tesseract_path: str = Field(
        default="/usr/local/bin/tesseract", description="Path to Tesseract executable"
    )
    ocr_tessdata_path: str = Field(
        default="/usr/local/share/tessdata", description="Path to Tesseract data"
    )
    ocr_dpi: int = Field(default=300, description="DPI for OCR processing")

    @field_validator("ocr_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate OCR language code."""
        valid_languages = [
            "eng",
            "hin",
            "san",
            "tam",
            "tel",
            "mal",
            "kan",
            "ben",
            "guj",
            "mar",
            "ori",
            "pun",
        ]
        if v not in valid_languages:
            raise ValueError(f"Invalid language. Must be one of: {', '.join(valid_languages)}")
        return v


class FileProcessingConfig(BaseSettings):
    """File processing configuration settings."""

    model_config = SettingsConfigDict(env_prefix="")

    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")
    supported_file_types: str = Field(
        default="pdf,xlsx,xls,docx,doc,jpg,jpeg,png,tiff,bmp",
        description="Comma-separated list of supported file types",
    )
    chunk_size: int = Field(default=8192, description="Chunk size for file reading")

    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return [ext.strip().lower() for ext in self.supported_file_types.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


class ClassificationConfig(BaseSettings):
    """Document classification configuration settings."""

    model_config = SettingsConfigDict(env_prefix="CLASSIFICATION_")

    auto_classify_enabled: bool = Field(default=True, description="Enable automatic classification")
    classification_model_path: str = Field(
        default="./models/classifier.pkl", description="Path to classification model"
    )
    classification_confidence_threshold: float = Field(
        default=0.7, description="Minimum confidence for classification"
    )

    @field_validator("classification_confidence_threshold")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        return v


class ReorganizationConfig(BaseSettings):
    """Reorganization configuration settings."""

    model_config = SettingsConfigDict(env_prefix="")

    default_folder_template: str = Field(default="standard", description="Default folder template")
    financial_year_start: str = Field(
        default="04-01", description="Financial year start date (MM-DD)"
    )
    create_undo_points: bool = Field(
        default=True, description="Create undo points before reorganization"
    )

    @field_validator("financial_year_start")
    @classmethod
    def validate_financial_year_start(cls, v: str) -> str:
        """Validate financial year start date format."""
        try:
            month, day = map(int, v.split("-"))
            if not (1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError("Invalid date")
        except Exception:
            raise ValueError("Financial year start must be in MM-DD format")
        return v


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(env_prefix="LOG_")

    log_level: str = Field(default="INFO", description="Logging level")
    log_path: str = Field(default="./logs", description="Path to log files")
    log_rotation: str = Field(default="10 MB", description="Log rotation size")
    log_retention: str = Field(default="30 days", description="Log retention period")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.upper()


class CacheConfig(BaseSettings):
    """Cache configuration settings."""

    model_config = SettingsConfigDict(env_prefix="CACHE_")

    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache time-to-live in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")


class PerformanceConfig(BaseSettings):
    """Performance configuration settings."""

    model_config = SettingsConfigDict(env_prefix="")

    indexing_threads: int = Field(default=4, description="Number of indexing threads")
    batch_size: int = Field(default=100, description="Batch size for operations")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")

    @field_validator("indexing_threads")
    @classmethod
    def validate_threads(cls, v: int) -> int:
        """Validate number of threads."""
        if v < 1:
            raise ValueError("Number of threads must be at least 1")
        return v


class JobQueueConfig(BaseSettings):
    """Job queue configuration settings."""

    model_config = SettingsConfigDict(env_prefix="JOB_QUEUE_")

    job_queue_enabled: bool = Field(default=True, description="Enable job queue")
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis URL for job queue"
    )
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0", description="Celery result backend"
    )
    max_retries: int = Field(default=3, description="Maximum job retry attempts")
    retry_backoff: int = Field(default=60, description="Retry backoff in seconds")
    worker_concurrency: int = Field(default=4, description="Number of concurrent workers")

    @field_validator("max_retries")
    @classmethod
    def validate_retries(cls, v: int) -> int:
        """Validate max retries."""
        if v < 0:
            raise ValueError("Max retries must be non-negative")
        return v


class AnalyticsConfig(BaseSettings):
    """Analytics configuration settings."""

    model_config = SettingsConfigDict(env_prefix="ANALYTICS_")

    analytics_enabled: bool = Field(default=True, description="Enable DuckDB analytics")
    analytics_cache_size_mb: int = Field(default=1024, description="Analytics cache size in MB")
    analytics_threads: int = Field(default=2, description="Number of analytics threads")

    @field_validator("analytics_cache_size_mb")
    @classmethod
    def validate_cache_size(cls, v: int) -> int:
        """Validate cache size."""
        if v < 128:
            raise ValueError("Cache size must be at least 128 MB")
        return v


class Settings(BaseSettings):
    """Main application settings combining all configuration sections."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    app_name: str = Field(default="CRMS", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(
        default="development", description="Environment (development/production)"
    )

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    ipc: IPCConfig = Field(default_factory=IPCConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    file_processing: FileProcessingConfig = Field(default_factory=FileProcessingConfig)
    classification: ClassificationConfig = Field(default_factory=ClassificationConfig)
    reorganization: ReorganizationConfig = Field(default_factory=ReorganizationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    job_queue: JobQueueConfig = Field(default_factory=JobQueueConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_environments = ["development", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(
                f"Invalid environment. Must be one of: {', '.join(valid_environments)}"
            )
        return v.lower()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create global settings instance
settings = get_settings()
