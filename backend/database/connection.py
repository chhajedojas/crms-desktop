"""
Database connection management for CRMS backend.
Handles SQLite and DuckDB database connections.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from core import DatabaseError, Settings, get_logger, get_settings

# Optional DuckDB import
try:
    import duckdb

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


class DatabaseConnection:
    """Manages database connections for SQLite and DuckDB."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize database connection with optional settings.

        Args:
            settings: Settings instance. If None, will use get_settings().
        """
        self.settings = settings or get_settings()
        self.logger = get_logger(__name__)
        self._sqlite_connection: Optional[sqlite3.Connection] = None
        self._duckdb_connection: Optional[Any] = None

    def _validate_path(self, path: Path) -> Path:
        """Validate that database path is within application directory.

        Args:
            path: Path to validate

        Returns:
            Resolved path

        Raises:
            DatabaseError: If path is outside application directory
        """
        resolved_path = path.resolve()
        cwd = Path.cwd().resolve()

        # Allow paths within current directory or its subdirectories
        if not str(resolved_path).startswith(str(cwd)):
            raise DatabaseError(
                f"Database path must be within application directory: {resolved_path}"
            )

        return resolved_path

    @contextmanager
    def get_sqlite_connection(self) -> Any:
        """Get SQLite database connection with context manager."""
        try:
            db_path = self._validate_path(Path(self.settings.database.database_path))
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(db_path), timeout=30, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"SQLite connection failed: {str(e)}", exc_info=True)
            raise DatabaseError(f"SQLite error: {str(e)}")
        except IOError as e:
            self.logger.error(f"File system error for SQLite: {str(e)}", exc_info=True)
            raise DatabaseError(f"File system error: {str(e)}")
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in SQLite connection: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to connect to SQLite database: {str(e)}")

    @contextmanager
    def get_duckdb_connection(self) -> Any:
        """Get DuckDB database connection with context manager."""
        if not DUCKDB_AVAILABLE:
            raise DatabaseError(
                "DuckDB is not available. Install duckdb package to use analytics features."
            )

        try:
            db_path = self._validate_path(Path(self.settings.database.duckdb_path))
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = duckdb.connect(str(db_path))
            yield conn
            conn.close()
        except (IOError, OSError) as e:
            self.logger.error(f"File system error for DuckDB: {str(e)}", exc_info=True)
            raise DatabaseError(f"File system error: {str(e)}")
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in DuckDB connection: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to connect to DuckDB database: {str(e)}")

    def initialize_sqlite(self, schema_path: str) -> None:
        """Initialize SQLite database with schema.

        Args:
            schema_path: Path to schema SQL file

        Raises:
            DatabaseError: If initialization fails
        """
        try:
            schema_file = Path(schema_path)
            if not schema_file.exists():
                raise DatabaseError(f"Schema file not found: {schema_path}")

            with self.get_sqlite_connection() as conn:
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
            self.logger.info(f"SQLite database initialized from schema: {schema_path}")
        except sqlite3.Error as e:
            self.logger.error(f"SQLite initialization failed: {str(e)}", exc_info=True)
            raise DatabaseError(f"SQLite error during initialization: {str(e)}")
        except IOError as e:
            self.logger.error(f"Failed to read schema file: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to read schema file: {str(e)}")
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during SQLite initialization: {str(e)}",
                exc_info=True,
            )
            raise DatabaseError(f"Failed to initialize SQLite database: {str(e)}")


# Global database connection instance (for backward compatibility)
# TODO: Remove global instance in v0.2 when dependency injection is fully implemented
db_connection = DatabaseConnection()
