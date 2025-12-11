from pydantic import BaseModel
from typing import Optional

class SubmissionOut(BaseModel):
    submission_id: str
    status: str
    is_correct: Optional[bool] = None
    awarded_coins: int = 0
