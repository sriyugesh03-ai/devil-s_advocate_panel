import pytest
from unittest.mock import AsyncMock
from backend.app.agents.vc_agent import SkepticalVCAgent
from backend.app.agents.financial_agent import FinancialAnalystAgent
from backend.app.agents.market_agent import MarketRealistAgent
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel

@pytest.mark.asyncio
async def test_specialist_agents_mocked():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = AgentChallenge(
        persona=AgentPersona.VC,
        reasoning_summary="Open-source packages offer similar features.",
        question="How will you build a defensive moat against OSS?",
        severity=SeverityLevel.CRITICAL,
        evidence_citation="Hamilton Helmer Scale Economies"
    )

    vc = SkepticalVCAgent(llm_service=mock_llm)
    pitch_sample = {
        "title": "FastAI",
        "tagline": "Faster AI",
        "problem": "Slow inference",
        "solution": "Fast inference",
        "business_model": "SaaS",
        "traction": "10 users",
        "competition": "vLLM"
    }

    challenge = await vc.generate_challenge(
        pitch=pitch_sample,
        round_number=1,
        rag_context="Hamilton Helmer Counter-Positioning",
        conversation_history=[]
    )

    assert challenge.persona == AgentPersona.VC
    assert challenge.severity == SeverityLevel.CRITICAL
