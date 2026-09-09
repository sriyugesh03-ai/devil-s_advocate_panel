import logging
from typing import Dict, Any, Optional
from backend.app.schemas.verdict import FinalVerdict
from backend.app.schemas.session import SessionStatus
from backend.app.agents.verdict_agent import VerdictAgent
from backend.app.services.session_service import session_service

logger = logging.getLogger(__name__)

class VerdictService:
    """Service to generate, persist, and fetch final investment verdicts."""

    def __init__(self):
        self.verdict_agent = VerdictAgent()

    async def generate_verdict_for_session(self, session_id: str) -> FinalVerdict:
        session = await session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # If already calculated, return cached
        if session.get("verdict"):
            return FinalVerdict.model_validate(session["verdict"])

        pitch = session.get("pitch", {})
        rounds_history = session.get("rounds_history", [])
        user_responses = session.get("user_responses", [])

        logger.info(f"Generating final investment verdict for session {session_id} ({pitch.get('title')})...")
        verdict = await self.verdict_agent.evaluate_full_session(
            pitch=pitch,
            rounds_history=rounds_history,
            user_responses=user_responses,
        )

        session["verdict"] = verdict.model_dump()
        session["status"] = SessionStatus.COMPLETED.value
        await session_service.update_session(session_id, session)

        return verdict

verdict_service = VerdictService()
