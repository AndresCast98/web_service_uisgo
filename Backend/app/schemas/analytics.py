from datetime import datetime
from pydantic import BaseModel
from typing import List
from uuid import UUID


class GroupStats(BaseModel):
    group_id: UUID
    group_name: str
    total_students: int
    responded_students: int
    response_rate: float
    total_activities: int
    total_submissions: int
    accuracy: float


class AnalyticsSummary(BaseModel):
    generated_at: datetime
    groups: List[GroupStats]
    total_groups: int
    total_students: int
    total_activities: int
    total_submissions: int
