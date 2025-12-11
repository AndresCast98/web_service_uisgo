import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..db.base_class import Base


class QuickAction(Base):
    __tablename__ = "quick_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False)
    subtitle = Column(Text)
    icon = Column(String(64))
    target_route = Column(String(128), nullable=False)
    allowed_roles = Column(String(128), nullable=False, default="student,professor,superuser")
    order_index = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    key = Column(String(64), primary_key=True)
    description = Column(Text)
    value = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
