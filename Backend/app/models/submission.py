import uuid, enum
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ..db.base_class import Base


class SubmissionStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answer = Column(JSONB)                 # {"selected":[1]} o {"text":"..."}
    is_correct = Column(Boolean)           # auto para quiz_single
    score = Column(Integer)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.submitted)
    awarded_coins = Column(Integer, default=0)
    graded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("activity_id", "user_id", name="uq_submission"),)
