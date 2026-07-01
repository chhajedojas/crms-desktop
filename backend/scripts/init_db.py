"""
Database initialization script for CRMS backend.
Initializes SQLite database with schema and seed data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ConfigurationError, get_logger, setup_logging  # noqa: E402
from database.connection import db_connection  # noqa: E402


def main():
    """Initialize the database."""
    logger = None
    try:
        # Setup logging
        setup_logging()
        logger = get_logger(__name__)

        logger.info("Starting database initialization...")

        # Get schema path
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"

        if not schema_path.exists():
            raise ConfigurationError(f"Schema file not found: {schema_path}")

        # Initialize SQLite database
        logger.info(f"Initializing SQLite database from schema: {schema_path}")
        db_connection.initialize_sqlite(str(schema_path))

        logger.info("Database initialization completed successfully")

    except Exception as e:
        if logger:
            logger.error(f"Database initialization failed: {str(e)}")
        else:
            print(f"Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
