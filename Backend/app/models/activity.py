import uuid, enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ..db.base_class import Base


class ActivityType(str, enum.Enum):
    quiz_single = "quiz_single"
    open = "open"

class QuestionType(str, enum.Enum):
    single = "single"
    open = "open"

class ActivityStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    closed = "closed"

class Activity(Base):
    __tablename__ = "activities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    type = Column(Enum(ActivityType), nullable=False, default=ActivityType.quiz_single)
    q_text = Column(String, nullable=False)
    q_type = Column(Enum(QuestionType), nullable=False, default=QuestionType.single)
    q_options = Column(JSONB)   # list[str]
    q_correct = Column(JSONB)   # list[int]
    coins_on_complete = Column(Integer, default=0)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.draft)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityTarget(Base):
    __tablename__ = "activity_targets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    __table_args__ = (UniqueConstraint("activity_id", "group_id", name="uq_activity_group"),)
