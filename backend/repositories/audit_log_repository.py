"""
Audit log repository implementation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from repositories.interfaces import AuditLogRepositoryInterface
from database.models import AuditLog as AuditLogModel
from database.mappers import AuditLogMapper
from core import get_logger
from domain import AuditLog


class AuditLogRepository(BaseRepository[AuditLog, AuditLogModel], AuditLogRepositoryInterface):
    """Repository for Audit Log entity."""

    def __init__(self, session: Session):
        """Initialize Audit Log repository with session, model, and mapper."""
        super().__init__(session, AuditLogModel, AuditLogMapper)
        self.logger = get_logger(__name__)
