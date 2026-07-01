"""
Relationship repository implementation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from repositories.interfaces import RelationshipRepositoryInterface
from database.models import Relationship as RelationshipModel
from database.mappers import RelationshipMapper
from domain import Relationship
from core import get_logger


class RelationshipRepository(BaseRepository[Relationship, RelationshipModel], RelationshipRepositoryInterface):
    """Repository for Relationship entity."""

    def __init__(self, session: Session):
        """Initialize Relationship repository with session, model, and mapper."""
        super().__init__(session, RelationshipModel, RelationshipMapper)
        self.logger = get_logger(__name__)
