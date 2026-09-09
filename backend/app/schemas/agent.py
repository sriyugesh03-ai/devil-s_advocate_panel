from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from enum import Enum

class AgentPersona(str, Enum):
    VC = "Skeptical VC"
    FINANCIAL = "Financial Analyst"
    MARKET = "Market Realist"

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AgentChallenge(BaseModel):
    persona: AgentPersona
    reasoning_summary: str = Field(..., description="User-facing concise summary explaining why the agent is skeptical")
    question: str = Field(..., description="The sharp, targeted interrogation question for the founder")
    severity: SeverityLevel = Field(default=SeverityLevel.HIGH, description="Estimated severity of this identified vulnerability")
    evidence_citation: Optional[str] = Field(default="", description="Industry benchmark, financial ratio, or case study citation")

class AgentReaction(BaseModel):
    persona: AgentPersona
    reaction_summary: str = Field(..., description="Agent critique on how well the founder addressed their challenge")
    satisfaction_score: int = Field(..., ge=0, le=100, description="Score 0-100 on how convincing the founder's response was")
    lingering_concern: Optional[str] = Field(default=None, description="Remaining vulnerability or follow-up focus")

class RoundInterrogation(BaseModel):
    round_number: int = Field(..., ge=1, le=3)
    challenges: List[AgentChallenge]
    founder_response: Optional[str] = None
    reactions: Optional[List[AgentReaction]] = None
