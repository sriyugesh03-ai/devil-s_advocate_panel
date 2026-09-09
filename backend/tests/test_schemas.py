import pytest
from backend.app.schemas.pitch import StartupPitchCreate, StartupPitch
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.schemas.verdict import FinalVerdict, PersonaScore, WeaknessItem
from backend.app.schemas.session import UserResponseSubmit, SessionStateResponse, SessionStatus

def test_startup_pitch_validation():
    valid_data = {
        "title": "QuantumFlow AI",
        "tagline": "Real-time AI pipeline acceleration",
        "problem": "AI models suffer from high inference latency and memory fragmentation during production serving.",
        "solution": "We use proprietary kernel optimizations and distributed memory pooling to reduce latency by 60%.",
        "target_market": "Enterprise AI infrastructure teams and LLM API providers with over $10B TAM.",
        "business_model": "Usage-based software license per GPU node hour with 85% gross margins.",
        "traction": "$25k MRR in closed beta",
        "competition": "vLLM, TensorRT-LLM",
        "fundraising_goal": "$2M Seed at $12M cap"
    }
    pitch = StartupPitchCreate(**valid_data)
    assert pitch.title == "QuantumFlow AI"
    assert pitch.business_model.startswith("Usage-based")

def test_agent_challenge_schema():
    challenge = AgentChallenge(
        persona=AgentPersona.VC,
        reasoning_summary="Open-source frameworks like vLLM are improving rapidly, threatening standalone kernel optimization moats.",
        question="How do you avoid getting commoditized when open-source maintainers implement similar kernel kernels?",
        severity=SeverityLevel.CRITICAL,
        evidence_citation="Hamilton Helmer Counter-Positioning & Process Power"
    )
    assert challenge.persona == AgentPersona.VC
    assert challenge.severity == SeverityLevel.CRITICAL

def test_verdict_schema():
    verdict = FinalVerdict(
        overall_score=72,
        investment_recommendation="Conditional Follow",
        executive_summary="Promising technical moat, but high risk of open-source commoditization and enterprise sales friction.",
        survival_odds_percentage=65,
        persona_scores=[
            PersonaScore(persona=AgentPersona.VC, score=68, verdict="Pass", key_takeaway="Moat defensibility remains questionable."),
            PersonaScore(persona=AgentPersona.FINANCIAL, score=80, verdict="Invest", key_takeaway="Strong 85% gross margins."),
            PersonaScore(persona=AgentPersona.MARKET, score=68, verdict="Pass", key_takeaway="Long enterprise POC cycles.")
        ],
        ranked_weaknesses=[
            WeaknessItem(
                title="Moat Vulnerability",
                category="Defensibility",
                severity=SeverityLevel.CRITICAL,
                description="Fast-moving OSS alternatives can erase performance advantages.",
                recommended_fix="Build proprietary enterprise integrations and workflow lock-in."
            )
        ],
        priority_action_plan=["Secure 3 paid enterprise LOIs", "Demonstrate 2x moat over latest vLLM release"]
    )
    assert verdict.overall_score == 72
    assert len(verdict.ranked_weaknesses) == 1
