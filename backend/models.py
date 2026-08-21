from pydantic import BaseModel
from typing import Optional

class CandidateResponse(BaseModel):
    id: str
    name: str
    category: str
    votes: int
    icon: Optional[str] = "⚡"

class VoteRequest(BaseModel):
    candidate_id: str
