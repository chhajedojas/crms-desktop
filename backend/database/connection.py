"""
Database connection management for CRMS backend.
Handles SQLite and DuckDB database connections.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from core import DatabaseError, get_settings

# Optional DuckDB import
try:
    import duckdb

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


class DatabaseConnection:
    """Manages database connections for SQLite and DuckDB."""

    def __init__(self):
        self.settings = get_settings()
        self._sqlite_connection: Optional[sqlite3.Connection] = None
        self._duckdb_connection: Optional[Any] = None

    @contextmanager
    def get_sqlite_connection(self) -> Any:
        """Get SQLite database connection with context manager."""
        try:
            db_path = Path(self.settings.database.database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(db_path), timeout=30, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.close()
        except Exception as e:
            raise DatabaseError(f"Failed to connect to SQLite database: {str(e)}")

    @contextmanager
    def get_duckdb_connection(self) -> Any:
        """Get DuckDB database connection with context manager."""
        if not DUCKDB_AVAILABLE:
            raise DatabaseError(
                "DuckDB is not available. Install duckdb package to use analytics features."
            )

        try:
            db_path = Path(self.settings.database.duckdb_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = duckdb.connect(str(db_path))
            yield conn
            conn.close()
        except Exception as e:
            raise DatabaseError(f"Failed to connect to DuckDB database: {str(e)}")

    def initialize_sqlite(self, schema_path: str) -> None:
        """Initialize SQLite database with schema."""
        try:
            with self.get_sqlite_connection() as conn:
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to initialize SQLite database: {str(e)}")


# Global database connection instance
db_connection = DatabaseConnection()
