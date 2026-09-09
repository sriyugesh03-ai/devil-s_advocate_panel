from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.agent import SeverityLevel, AgentPersona

class WeaknessItem(BaseModel):
    title: str = Field(..., description="Short descriptive title of the vulnerability")
    category: str = Field(..., description="E.g., Moat & Defensibility, Unit Economics, GTM & Adoption")
    severity: SeverityLevel = Field(..., description="Severity rank: Critical, High, Medium, Low")
    description: str = Field(..., description="Detailed explanation of the risk or weakness")
    recommended_fix: str = Field(..., description="Tactical, actionable pivot or mitigation step for the founder")

class PersonaScore(BaseModel):
    persona: AgentPersona
    score: int = Field(..., ge=0, le=100, description="Final score awarded by this agent (0-100)")
    verdict: str = Field(..., description="Short verdict statement from this agent's perspective")
    key_takeaway: str = Field(..., description="Primary reason for the score")

class FinalVerdict(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Consolidated panel score out of 100")
    investment_recommendation: str = Field(..., description="E.g., Pass, Strong Pass, Conditional Follow, Angel Bet")
    executive_summary: str = Field(..., description="High-level investment committee summary")
    survival_odds_percentage: int = Field(..., ge=0, le=100, description="Estimated 24-month survival/traction probability")
    persona_scores: List[PersonaScore] = Field(..., description="Score breakdown by individual specialist persona")
    ranked_weaknesses: List[WeaknessItem] = Field(..., description="All identified weaknesses ranked by severity")
    priority_action_plan: List[str] = Field(..., description="Top 3-5 high-priority steps to de-risk the venture before real investor pitches")
