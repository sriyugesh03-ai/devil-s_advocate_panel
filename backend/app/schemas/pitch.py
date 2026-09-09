from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List

class StartupPitchCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, description="Startup or product name")
    tagline: str = Field(..., min_length=5, max_length=250, description="One-liner explaining what the product does")
    problem: str = Field(..., min_length=20, max_length=2000, description="Core customer pain point being solved")
    solution: str = Field(..., min_length=20, max_length=2000, description="How your product uniquely solves this problem")
    target_market: str = Field(..., min_length=10, max_length=1500, description="Target customer segments and estimated TAM/SAM")
    business_model: str = Field(..., min_length=10, max_length=1500, description="Monetization model, pricing, and gross margin expectations")
    traction: Optional[str] = Field(default="Pre-revenue / Early stage", max_length=1000, description="Current revenue, users, waitlist, or growth metrics")
    competition: Optional[str] = Field(default="", max_length=1500, description="Existing incumbents and alternatives")
    fundraising_goal: Optional[str] = Field(default="", max_length=200, description="Amount seeking to raise and target valuation")

    @field_validator("title", "tagline", "problem", "solution")
    @classmethod
    def check_not_empty_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be blank or only whitespace.")
        return v.strip()

class StartupPitch(StartupPitchCreate):
    id: str = Field(..., description="Unique pitch identifier")
    created_at: str = Field(..., description="ISO 8601 timestamp")
