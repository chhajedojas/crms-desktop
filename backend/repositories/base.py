"""
Repository pattern base class for CRMS.

This module provides the base repository class that defines the interface
for all repositories in the system. It implements common CRUD operations
and provides a consistent interface for data access.

Repositories return domain entities, not ORM models, to maintain
clean separation between domain and persistence layers.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Type, TypeVar as GenericTypeVar
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core import get_logger
from database.exceptions import (
    RepositoryError,
    EntityNotFoundError,
    DuplicateEntityError,
    InvalidEntityError,
)

# Generic type for domain entities
DomainEntity = GenericTypeVar("DomainEntity")

# Generic type for ORM models
ORMModel = GenericTypeVar("ORMModel")


class BaseRepository(Generic[DomainEntity, ORMModel], ABC):
    """Base repository class with common CRUD operations.

    This repository returns domain entities, not ORM models, to maintain
    clean architecture where the domain layer has no knowledge of
    infrastructure details.
    """

    def __init__(self, session: Session, model: Type[ORMModel], mapper):
        """
        Initialize repository with database session, model, and mapper.

        Args:
            session: SQLAlchemy database session
            model: SQLAlchemy ORM model class
            mapper: Mapper class for converting between ORM and domain entities
        """
        self.session = session
        self.model = model
        self.mapper = mapper
        self.logger = get_logger(__name__)

    def get_by_id(self, entity_id: int) -> Optional[DomainEntity]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Domain entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Getting {self.model.__name__} by id: {entity_id}")
            stmt = select(self.model).where(self.model.id == entity_id)
            orm_entity = self.session.execute(stmt).scalar_one_or_none()
            if orm_entity:
                return self.mapper.to_domain(orm_entity)
            return None
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by id {entity_id}: {str(e)}", exc_info=True)
            raise RepositoryError(f"Failed to get {self.model.__name__}: {str(e)}")

    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[DomainEntity]:
        """
        Get all entities with optional pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of domain entities

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Getting all {self.model.__name__} entities")
            stmt = select(self.model)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            orm_entities = self.session.execute(stmt).scalars().all()
            return self.mapper.to_domain_list(list(orm_entities))
        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__} entities: {str(e)}", exc_info=True)
            raise RepositoryError(f"Failed to get {self.model.__name__} entities: {str(e)}")

    def create(self, entity: DomainEntity) -> DomainEntity:
        """
        Create a new entity.

        Args:
            entity: Domain entity to create

        Returns:
            Created domain entity with ID assigned

        Raises:
            InvalidEntityError: If entity is invalid
            DuplicateEntityError: If entity already exists
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Creating {self.model.__name__}")
            orm_entity = self.mapper.to_model(entity)
            self.session.add(orm_entity)
            self.session.flush()
            self.session.refresh(orm_entity)
            return self.mapper.to_domain(orm_entity)
        except Exception as e:
            self.session.rollback()
            error_msg = str(e)
            if "UNIQUE constraint" in error_msg or "duplicate" in error_msg.lower():
                self.logger.warning(f"Duplicate {self.model.__name__}: {error_msg}")
                raise DuplicateEntityError(f"{self.model.__name__} already exists")
            elif "NOT NULL" in error_msg or "constraint" in error_msg.lower():
                self.logger.warning(f"Invalid {self.model.__name__}: {error_msg}")
                raise InvalidEntityError(f"Invalid {self.model.__name__}: {error_msg}")
            else:
                self.logger.error(f"Error creating {self.model.__name__}: {error_msg}", exc_info=True)
                raise RepositoryError(f"Failed to create {self.model.__name__}: {error_msg}")

    def update(self, entity: DomainEntity) -> DomainEntity:
        """
        Update an existing entity.

        Args:
            entity: Domain entity to update

        Returns:
            Updated domain entity

        Raises:
            EntityNotFoundError: If entity not found
            InvalidEntityError: If entity is invalid
            RepositoryError: If database operation fails
        """
        try:
            if not entity.id:
                raise InvalidEntityError(f"{self.model.__name__} must have an ID to update")

            self.logger.debug(f"Updating {self.model.__name__} with id: {entity.id}")
            orm_entity = self.mapper.to_model(entity)
            self.session.merge(orm_entity)
            self.session.flush()
            self.session.refresh(orm_entity)
            return self.mapper.to_domain(orm_entity)
        except Exception as e:
            self.session.rollback()
            error_msg = str(e)
            if "NOT NULL" in error_msg or "constraint" in error_msg.lower():
                self.logger.warning(f"Invalid {self.model.__name__}: {error_msg}")
                raise InvalidEntityError(f"Invalid {self.model.__name__}: {error_msg}")
            else:
                self.logger.error(f"Error updating {self.model.__name__}: {error_msg}", exc_info=True)
                raise RepositoryError(f"Failed to update {self.model.__name__}: {error_msg}")

    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Deleting {self.model.__name__} with id: {entity_id}")
            stmt = delete(self.model).where(self.model.id == entity_id)
            result = self.session.execute(stmt)
            return result.rowcount > 0
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} with id {entity_id}: {str(e)}", exc_info=True)
            raise RepositoryError(f"Failed to delete {self.model.__name__}: {str(e)}")

    def count(self) -> int:
        """
        Count all entities.

        Returns:
            Number of entities

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Counting {self.model.__name__} entities")
            from sqlalchemy import func

            stmt = select(func.count()).select_from(self.model)
            result = self.session.execute(stmt).scalar()
            return result
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__} entities: {str(e)}", exc_info=True)
            raise RepositoryError(f"Failed to count {self.model.__name__} entities: {str(e)}")

    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if entity exists, False otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            self.logger.debug(f"Checking if {self.model.__name__} exists with id: {entity_id}")
            stmt = select(self.model.id).where(self.model.id == entity_id)
            result = self.session.execute(stmt).scalar_one_or_none()
            return result is not None
        except Exception as e:
            self.logger.error(f"Error checking if {self.model.__name__} exists: {str(e)}", exc_info=True)
            raise RepositoryError(f"Failed to check {self.model.__name__} existence: {str(e)}")
