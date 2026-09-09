from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from backend.app.schemas.pitch import StartupPitch
from backend.app.schemas.agent import RoundInterrogation
from backend.app.schemas.verdict import FinalVerdict

class SessionStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user_response"
    EVALUATING_ROUND = "evaluating_round"
    COMPLETED = "completed"
    FAILED = "failed"

class UserResponseSubmit(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    round_number: int = Field(..., ge=1, le=3, description="Current round number being answered")
    response_text: str = Field(..., min_length=10, max_length=5000, description="Founder's defense and answers to the panel's challenges")

class SessionStateResponse(BaseModel):
    session_id: str
    thread_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    pitch: StartupPitch
    current_round: int
    total_rounds: int = 3
    status: SessionStatus
    rounds: List[RoundInterrogation] = []
    verdict: Optional[FinalVerdict] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None

