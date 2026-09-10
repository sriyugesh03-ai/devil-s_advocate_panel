import asyncio
import logging
from typing import Dict, Any, Optional, List
from backend.app.schemas.session import SessionStatus
from backend.app.services.session_service import session_service
from backend.app.agents.vc_agent import SkepticalVCAgent
from backend.app.agents.financial_agent import FinancialAnalystAgent
from backend.app.agents.market_agent import MarketRealistAgent
from backend.app.services.verdict_service import verdict_service
from backend.app.rag.service import rag_service

logger = logging.getLogger(__name__)

class DebateEngineService:
    """Orchestrates multi-round debate progression and adversarial follow-ups."""

    def __init__(self):
        self.vc = SkepticalVCAgent()
        self.financial = FinancialAnalystAgent()
        self.market = MarketRealistAgent()

    def _get_fallback_challenge(self, persona: str, pitch: Dict[str, Any], round_number: int) -> Dict[str, Any]:
        """Generates contextual fallback challenges if LLM call fails or times out."""
        title = pitch.get("title", "this venture")
        target = pitch.get("target_market", "target market")
        model = pitch.get("business_model", "business model")
        
        if "VC" in persona:
            return {
                "persona": "Skeptical VC",
                "reasoning_summary": f"Your defensibility and moat in {target} require concrete proof against copycats.",
                "question": f"In Round {round_number}, what prevents well-capitalized incumbents or fast-followers from duplicating {title}'s core feature set within 60 days?",
                "severity": "Critical",
                "evidence_citation": "Hamilton Helmer 7 Powers: Scale Economies & Counter-Positioning"
            }
        elif "Financial" in persona:
            return {
                "persona": "Financial Analyst",
                "reasoning_summary": f"Your unit economic assumptions under {model} may not sustain high customer acquisition friction.",
                "question": f"Under stress in Round {round_number}, how does your CAC payback and gross margin hold up if paid acquisition costs double?",
                "severity": "High",
                "evidence_citation": "B2B SaaS Benchmark: 12-month CAC Payback Rule"
            }
        else:
            return {
                "persona": "Market Realist",
                "reasoning_summary": f"Market adoption inertia in {target} is significantly slower than early traction suggests.",
                "question": f"What is the single biggest operational or regulatory friction preventing enterprise buyers from deploying {title} today?",
                "severity": "High",
                "evidence_citation": "Crossing the Chasm: Mainstream Pragmatist Friction"
            }

    async def submit_and_advance_round(
        self,
        session_id: str,
        round_number: int,
        founder_response: str
    ) -> Dict[str, Any]:
        session = await session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session.get("status") == SessionStatus.COMPLETED.value and session.get("verdict"):
            return session

        pitch = session.get("pitch", {})
        current_challenges = session.get("current_challenges", [])
        total_rounds = session.get("total_rounds", 3)

        # 1. Generate reactions from all 3 specialist agents in parallel
        reaction_tasks = []
        for ch in current_challenges:
            persona = ch.get("persona", "")
            q = ch.get("question", "")
            if "VC" in str(persona):
                reaction_tasks.append(self.vc.generate_reaction(pitch, round_number, q, founder_response))
            elif "Financial" in str(persona):
                reaction_tasks.append(self.financial.generate_reaction(pitch, round_number, q, founder_response))
            elif "Market" in str(persona):
                reaction_tasks.append(self.market.generate_reaction(pitch, round_number, q, founder_response))

        raw_reactions = await asyncio.gather(*reaction_tasks, return_exceptions=True)
        
        valid_reactions = []
        for i, r in enumerate(raw_reactions):
            if hasattr(r, "model_dump"):
                valid_reactions.append(r.model_dump())
            else:
                persona_name = current_challenges[i].get("persona", "Panelist") if i < len(current_challenges) else "Panelist"
                valid_reactions.append({
                    "persona": persona_name,
                    "reaction_summary": f"Response noted. The panel remains cautious about execution risks in Round {round_number}.",
                    "satisfaction_score": 55,
                    "lingering_concern": "Execution and defensibility"
                })

        # 2. Archive this round in rounds_history
        completed_round_record = {
            "round_number": round_number,
            "challenges": current_challenges,
            "founder_response": founder_response,
            "reactions": valid_reactions
        }
        
        rounds_history = list(session.get("rounds_history", []))
        rounds_history.append(completed_round_record)
        
        user_responses = list(session.get("user_responses", []))
        user_responses.append({
            "round_number": round_number,
            "response_text": founder_response
        })

        session["rounds_history"] = rounds_history
        session["user_responses"] = user_responses
        session["current_reactions"] = valid_reactions

        # 3. Check if more rounds remain
        if round_number < total_rounds:
            next_round = round_number + 1
            session["current_round"] = next_round
            session["status"] = SessionStatus.IN_PROGRESS.value
            await session_service.update_session(session_id, session)

            # Retrieve refreshed domain context
            rag_contexts = {}
            try:
                rag_contexts = await rag_service.get_contexts_for_pitch(pitch)
            except Exception as re:
                logger.warning(f"RAG retrieval warning for session {session_id}: {re}")
            session["retrieved_contexts"] = rag_contexts

            # Generate next round challenges in parallel with history context
            next_challenge_tasks = [
                self.vc.generate_challenge(pitch, next_round, rag_contexts.get("vc", ""), rounds_history),
                self.financial.generate_challenge(pitch, next_round, rag_contexts.get("financial", ""), rounds_history),
                self.market.generate_challenge(pitch, next_round, rag_contexts.get("market", ""), rounds_history),
            ]
            raw_next_challenges = await asyncio.gather(*next_challenge_tasks, return_exceptions=True)
            
            personas = ["Skeptical VC", "Financial Analyst", "Market Realist"]
            valid_next_challenges = []
            for i, c in enumerate(raw_next_challenges):
                if hasattr(c, "model_dump"):
                    valid_next_challenges.append(c.model_dump())
                else:
                    logger.warning(f"Agent challenge generation fallback triggered for {personas[i]}: {c}")
                    valid_next_challenges.append(self._get_fallback_challenge(personas[i], pitch, next_round))

            session["current_challenges"] = valid_next_challenges
            session["status"] = SessionStatus.AWAITING_USER.value
            await session_service.update_session(session_id, session)
            return session
        else:
            # All 3 rounds complete -> auto-generate final verdict and mark completed
            session["current_challenges"] = []
            session["status"] = SessionStatus.COMPLETED.value
            await session_service.update_session(session_id, session)
            
            try:
                verdict = await verdict_service.generate_verdict_for_session(session_id)
                session["verdict"] = verdict.model_dump()
            except Exception as ve:
                logger.error(f"Error auto-generating verdict for session {session_id}: {ve}")
                
            return session

debate_service = DebateEngineService()

