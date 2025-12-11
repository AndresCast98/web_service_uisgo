import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..db.base_class import Base


class InviteCode(Base):
    __tablename__ = "invite_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
