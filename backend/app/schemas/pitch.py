from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List

class StartupPitchCreate(BaseModel):
    title: str = Field(default="My Startup", description="Startup or product name")
    tagline: str = Field(default="Innovative solution for the market", description="One-liner explaining what the product does")
    problem: str = Field(default="", description="Core customer pain point being solved")
    solution: str = Field(default="", description="How your product uniquely solves this problem")
    target_market: str = Field(default="", description="Target customer segments and estimated TAM/SAM")
    business_model: str = Field(default="", description="Monetization model, pricing, and gross margin expectations")
    traction: Optional[str] = Field(default="Pre-revenue / Early stage", description="Current revenue, users, waitlist, or growth metrics")
    competition: Optional[str] = Field(default="", description="Existing incumbents and alternatives")
    fundraising_goal: Optional[str] = Field(default="", description="Amount seeking to raise and target valuation")
    github_url: Optional[str] = Field(default="", description="Optional GitHub repository link for technical diligence")
    pitch_deck_filename: Optional[str] = Field(default="", description="Optional uploaded pitch deck filename")

    @field_validator("*", mode="before")
    @classmethod
    def sanitize_fields(cls, v: Any) -> Any:
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            return ", ".join(str(item) for item in v)
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            return "Untitled Startup"
        return v.strip()[:300]

    @field_validator("tagline")
    @classmethod
    def validate_tagline(cls, v: str) -> str:
        if not v or not v.strip():
            return "Innovative solution for target market"
        return v.strip()[:1000]

    @field_validator("problem")
    @classmethod
    def validate_problem(cls, v: str) -> str:
        if not v or not v.strip():
            return "Operational inefficiencies and high friction in current market workflows."
        return v.strip()[:10000]

    @field_validator("solution")
    @classmethod
    def validate_solution(cls, v: str) -> str:
        if not v or not v.strip():
            return "An integrated platform automating workflows to deliver superior speed and ROI."
        return v.strip()[:10000]

    @field_validator("target_market")
    @classmethod
    def validate_target_market(cls, v: str) -> str:
        if not v or not v.strip():
            return "Early adopters and growth enterprises in the domain."
        return v.strip()[:10000]

    @field_validator("business_model")
    @classmethod
    def validate_business_model(cls, v: str) -> str:
        if not v or not v.strip():
            return "Subscription SaaS and tiered usage pricing."
        return v.strip()[:10000]

    @field_validator("fundraising_goal")
    @classmethod
    def validate_fundraising(cls, v: Optional[str]) -> str:
        if not v or not str(v).strip():
            return "Seeking Seed / Series A funding"
        return str(v).strip()[:2000]

class StartupPitch(StartupPitchCreate):
    id: str = Field(..., description="Unique pitch identifier")
    created_at: str = Field(..., description="ISO 8601 timestamp")
