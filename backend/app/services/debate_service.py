import asyncio
import logging
from typing import Dict, Any, Optional
from backend.app.schemas.session import SessionStatus
from backend.app.services.session_service import session_service
from backend.app.agents.vc_agent import SkepticalVCAgent
from backend.app.agents.financial_agent import FinancialAnalystAgent
from backend.app.agents.market_agent import MarketRealistAgent
from backend.app.rag.service import rag_service

logger = logging.getLogger(__name__)

class DebateEngineService:
    """Orchestrates multi-round debate progression and adversarial follow-ups."""

    def __init__(self):
        self.vc = SkepticalVCAgent()
        self.financial = FinancialAnalystAgent()
        self.market = MarketRealistAgent()

    async def submit_and_advance_round(
        self,
        session_id: str,
        round_number: int,
        founder_response: str
    ) -> Dict[str, Any]:
        session = await session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session.get("status") == SessionStatus.COMPLETED.value:
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
        valid_reactions = [
            r.model_dump() if hasattr(r, "model_dump") else {
                "persona": "Panelist",
                "reaction_summary": "Response noted with skepticism.",
                "satisfaction_score": 50
            }
            for r in raw_reactions
        ]

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
            rag_contexts = await rag_service.get_contexts_for_pitch(pitch)
            session["retrieved_contexts"] = rag_contexts

            # Generate next round challenges in parallel with history context
            next_challenge_tasks = [
                self.vc.generate_challenge(pitch, next_round, rag_contexts.get("vc", ""), rounds_history),
                self.financial.generate_challenge(pitch, next_round, rag_contexts.get("financial", ""), rounds_history),
                self.market.generate_challenge(pitch, next_round, rag_contexts.get("market", ""), rounds_history),
            ]
            raw_next_challenges = await asyncio.gather(*next_challenge_tasks, return_exceptions=True)
            valid_next_challenges = [
                c.model_dump() for c in raw_next_challenges if hasattr(c, "model_dump")
            ]

            session["current_challenges"] = valid_next_challenges
            session["status"] = SessionStatus.AWAITING_USER.value
            await session_service.update_session(session_id, session)
            return session
        else:
            # All 3 rounds complete!
            session["current_challenges"] = []
            session["status"] = SessionStatus.EVALUATING_ROUND.value
            await session_service.update_session(session_id, session)
            return session

debate_service = DebateEngineService()
