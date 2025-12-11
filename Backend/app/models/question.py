import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..db.base_class import Base


class QuestionType(str, enum.Enum):
    open = "open"
    single = "single"


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(64), nullable=False, index=True)
    type = Column(String(16), nullable=False, default=QuestionType.open.value)
    options = Column(JSONB)
    reward_credits = Column(Integer, default=0)
    reward_coins = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuestionResponse(Base):
    __tablename__ = "question_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    answer = Column(JSONB)
    credits_awarded = Column(Integer, default=0)
    coins_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuestionCredit(Base):
    __tablename__ = "question_credits"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    balance = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QuestionTarget(Base):
    __tablename__ = "question_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("question_id", "group_id", name="uq_question_group"),)
