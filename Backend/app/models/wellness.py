import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..db.base_class import Base


class WellnessPrompt(Base):
    __tablename__ = "wellness_prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    options = Column(JSONB, nullable=False)
    screen = Column(String(64), nullable=False)
    frequency = Column(String(32), nullable=False, default="daily")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserMood(Base):
    __tablename__ = "user_moods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    prompt_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    mood_value = Column(String(64), nullable=False)
    extra_data = Column(JSONB)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)


class WellnessCenter(Base):
    __tablename__ = "wellness_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(JSONB)
    contact = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class WellnessTurn(Base):
    __tablename__ = "wellness_turns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String(32), nullable=False, default="waiting")
    qr_token = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
