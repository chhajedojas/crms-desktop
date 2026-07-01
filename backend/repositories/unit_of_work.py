"""
Unit of Work pattern implementation for CRMS.

This module provides the Unit of Work pattern for managing transactions
and coordinating repository operations. It ensures that all operations
within a unit of work are atomic and can be committed or rolled back.
"""

from contextlib import contextmanager
from typing import Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from core import get_logger, get_settings
from database.exceptions import TransactionError
from database.models import Base


class UnitOfWork:
    """
    Unit of Work for managing database transactions.

    This class provides a context manager for database sessions and
    coordinates repository operations within a transaction.
    """

    def __init__(self, session_factory: Optional[sessionmaker] = None):
        """
        Initialize Unit of Work with optional session factory.

        Args:
            session_factory: SQLAlchemy session factory. If None, creates from settings.
        """
        self.logger = get_logger(__name__)
        self.settings = get_settings()

        if session_factory:
            self.session_factory = session_factory
        else:
            # Create session factory from settings
            db_url = f"sqlite:///{self.settings.database.database_path}"
            engine = create_engine(
                db_url,
                echo=False,
                connect_args={"check_same_thread": False},
            )
            self.session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

        self._session: Optional[Session] = None

    @contextmanager
    def session_scope(self) -> Session:
        """
        Provide a transactional scope around a series of operations.

        Yields:
            SQLAlchemy session

        Raises:
            TransactionError: If transaction fails
        """
        session = self.session_factory()
        try:
            self.logger.debug("Starting database session")
            yield session
            session.commit()
            self.logger.debug("Database session committed successfully")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session rolled back due to error: {str(e)}", exc_info=True)
            raise TransactionError(f"Transaction failed: {str(e)}")
        finally:
            session.close()
            self.logger.debug("Database session closed")

    def begin(self) -> Session:
        """
        Begin a new transaction and return the session.

        Returns:
            SQLAlchemy session

        Raises:
            TransactionError: If session creation fails
        """
        try:
            self.logger.debug("Beginning new transaction")
            self._session = self.session_factory()
            return self._session
        except Exception as e:
            self.logger.error(f"Failed to begin transaction: {str(e)}", exc_info=True)
            raise TransactionError(f"Failed to begin transaction: {str(e)}")

    def commit(self) -> None:
        """
        Commit the current transaction.

        Raises:
            TransactionError: If commit fails or no active session
        """
        if not self._session:
            raise TransactionError("No active session to commit")

        try:
            self.logger.debug("Committing transaction")
            self._session.commit()
            self.logger.debug("Transaction committed successfully")
        except Exception as e:
            self.logger.error(f"Failed to commit transaction: {str(e)}", exc_info=True)
            raise TransactionError(f"Failed to commit transaction: {str(e)}")

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Raises:
            TransactionError: If rollback fails or no active session
        """
        if not self._session:
            raise TransactionError("No active session to rollback")

        try:
            self.logger.debug("Rolling back transaction")
            self._session.rollback()
            self.logger.debug("Transaction rolled back successfully")
        except Exception as e:
            self.logger.error(f"Failed to rollback transaction: {str(e)}", exc_info=True)
            raise TransactionError(f"Failed to rollback transaction: {str(e)}")

    def close(self) -> None:
        """
        Close the current session.

        Raises:
            TransactionError: If close fails or no active session
        """
        if not self._session:
            return

        try:
            self.logger.debug("Closing session")
            self._session.close()
            self._session = None
            self.logger.debug("Session closed successfully")
        except Exception as e:
            self.logger.error(f"Failed to close session: {str(e)}", exc_info=True)
            raise TransactionError(f"Failed to close session: {str(e)}")

    def __enter__(self) -> "UnitOfWork":
        """Enter context manager."""
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager with automatic commit or rollback."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
