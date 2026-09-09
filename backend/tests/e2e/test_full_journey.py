import pytest
from unittest.mock import AsyncMock, patch
from backend.app.schemas.pitch import StartupPitchCreate
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.schemas.verdict import FinalVerdict, PersonaScore, WeaknessItem
from backend.app.services.session_service import session_service
from backend.app.services.debate_service import debate_service
from backend.app.services.verdict_service import verdict_service
from backend.app.pdf.generator import pdf_generator

@pytest.mark.asyncio
async def test_end_to_end_panel_gauntlet():
    # 1. Pitch submission
    pitch_data = {
        "title": "AegisAI Cloud",
        "tagline": "Real-time AI Kubernetes security & auto-remediation",
        "problem": "Kubernetes misconfigurations cause 70% of enterprise cloud breaches.",
        "solution": "Continuous eBPF cluster scanning and automated least-privilege policy generation.",
        "target_market": "Fortune 2000 cloud engineering teams ($8B TAM).",
        "business_model": "$50/node/month with 80% SaaS gross margin.",
        "traction": "$40k MRR across 5 pilot customers.",
        "competition": "Wiz, Palo Alto Prisma Cloud, Orca Security",
        "fundraising_goal": "$3M Seed round"
    }

    # Mock the LLM calls to test the entire multi-agent state flow deterministically
    mock_challenge = AgentChallenge(
        persona=AgentPersona.VC,
        reasoning_summary="Wiz and Prisma Cloud already bundle eBPF runtime security for enterprise accounts.",
        question="Why would an enterprise buyer purchase AegisAI instead of enabling Wiz's bundled runtime agent?",
        severity=SeverityLevel.CRITICAL,
        evidence_citation="Hamilton Helmer Counter-Positioning & Scale Economies"
    )

    mock_reaction = AgentReaction(
        persona=AgentPersona.VC,
        reaction_summary="Good distinction on deep eBPF kernel enforcement, but distribution remains the primary obstacle.",
        satisfaction_score=75,
        lingering_concern="Enterprise procurement friction"
    )

    with patch("backend.app.agents.vc_agent.SkepticalVCAgent.generate_challenge", AsyncMock(return_value=mock_challenge)), \
         patch("backend.app.agents.financial_agent.FinancialAnalystAgent.generate_challenge", AsyncMock(return_value=mock_challenge)), \
         patch("backend.app.agents.market_agent.MarketRealistAgent.generate_challenge", AsyncMock(return_value=mock_challenge)), \
         patch("backend.app.agents.vc_agent.SkepticalVCAgent.generate_reaction", AsyncMock(return_value=mock_reaction)), \
         patch("backend.app.agents.financial_agent.FinancialAnalystAgent.generate_reaction", AsyncMock(return_value=mock_reaction)), \
         patch("backend.app.agents.market_agent.MarketRealistAgent.generate_reaction", AsyncMock(return_value=mock_reaction)):

        # Step 1: Create Session (Round 1)
        session = await session_service.create_session(pitch_data)
        session_id = session["session_id"]
        assert session["current_round"] == 1
        assert len(session["current_challenges"]) == 3

        # Step 2: Founder answers Round 1 -> Advances to Round 2
        r1_response = "We integrate directly at the Linux kernel level and provide 10x faster remediation than Wiz."
        session_r2 = await debate_service.submit_and_advance_round(session_id, 1, r1_response)
        assert session_r2["current_round"] == 2
        assert len(session_r2["rounds_history"]) == 1

        # Step 3: Founder answers Round 2 -> Advances to Round 3
        r2_response = "Our CAC is under $8k due to open-source developer-led adoption."
        session_r3 = await debate_service.submit_and_advance_round(session_id, 2, r2_response)
        assert session_r3["current_round"] == 3
        assert len(session_r3["rounds_history"]) == 2

        # Step 4: Founder answers Round 3 -> Gauntlet complete
        r3_response = "We have 3 design partners committing to 3-year contracts upon GA."
        session_final = await debate_service.submit_and_advance_round(session_id, 3, r3_response)
        assert len(session_final["rounds_history"]) == 3

        # Step 5: Synthesize Final Verdict
        verdict = await verdict_service.generate_verdict_for_session(session_id)
        assert verdict.overall_score > 0
        assert len(verdict.persona_scores) == 3
        assert len(verdict.ranked_weaknesses) > 0

        # Step 6: Generate PDF Report
        full_session = await session_service.get_session(session_id)
        pdf_stream = pdf_generator.generate_report(full_session)
        assert pdf_stream.getvalue().startswith(b"%PDF")
