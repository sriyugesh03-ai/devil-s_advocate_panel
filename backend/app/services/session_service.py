import datetime
import logging
from typing import Dict, Any, Optional, List
from backend.app.graph.interrupts import generate_session_id, generate_thread_id
from backend.app.graph.graph import panel_graph
from backend.app.graph.checkpointer import MongoStateCheckpointer
from backend.app.schemas.session import SessionStatus, SessionStateResponse
from backend.app.schemas.pitch import StartupPitch
from backend.app.db.mongo import get_db

logger = logging.getLogger(__name__)

class SessionService:
    """Manages the full lifecycle of a Devil's Advocate Panel session with MongoDB persistence."""

    # In-memory session store for local fallback when MongoDB is not running
    _in_memory_sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    async def create_session(cls, pitch_data: Dict[str, Any], user_id: Optional[str] = None, user_email: Optional[str] = None) -> Dict[str, Any]:
        session_id = generate_session_id()
        thread_id = generate_thread_id(session_id)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        pitch_record = {
            **pitch_data,
            "id": f"pitch_{session_id}",
            "created_at": now_iso
        }

        initial_state = {
            "session_id": session_id,
            "thread_id": thread_id,
            "user_id": user_id,
            "user_email": user_email,
            "pitch": pitch_record,
            "current_round": 1,
            "total_rounds": 3,
            "status": SessionStatus.IN_PROGRESS.value,
            "retrieved_contexts": {},
            "current_challenges": [],
            "user_responses": [],
            "current_reactions": [],
            "rounds_history": [],
            "verdict": None,
            "created_at": now_iso,
            "updated_at": now_iso,
            "error_message": None
        }

        # Save session
        cls._in_memory_sessions[session_id] = initial_state
        await MongoStateCheckpointer.save_session_state(session_id, initial_state)


        # Run Graph for Round 1
        try:
            config = {"configurable": {"thread_id": thread_id}}
            result = await panel_graph.ainvoke(
                {
                    "session_id": session_id,
                    "thread_id": thread_id,
                    "pitch": pitch_record,
                    "current_round": 1,
                    "total_rounds": 3,
                    "rounds_history": [],
                },
                config=config
            )

            # Update session state with generated challenges
            updated_state = cls._in_memory_sessions[session_id]
            updated_state["current_challenges"] = result.get("current_challenges", [])
            updated_state["status"] = SessionStatus.AWAITING_USER.value
            updated_state["retrieved_contexts"] = result.get("retrieved_contexts", {})
            updated_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

            cls._in_memory_sessions[session_id] = updated_state
            await MongoStateCheckpointer.save_session_state(session_id, updated_state)

            return updated_state

        except Exception as e:
            logger.error(f"Error starting session graph: {e}")
            initial_state["status"] = SessionStatus.FAILED.value
            initial_state["error_message"] = str(e)
            cls._in_memory_sessions[session_id] = initial_state
            return initial_state

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        # Check MongoDB first
        state = await MongoStateCheckpointer.get_session_state(session_id)
        if state:
            cls._in_memory_sessions[session_id] = state
            return state
        return cls._in_memory_sessions.get(session_id)

    @classmethod
    async def list_user_sessions(cls, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all sessions belonging to the user or all available sessions."""
        db = get_db()
        if db is not None:
            try:
                query = {"user_id": user_id} if user_id else {}
                cursor = db.sessions.find(query, {"_id": 0}).sort("created_at", -1)
                return await cursor.to_list(length=100)
            except Exception as e:
                logger.error(f"Error querying user sessions from MongoDB: {e}")

        # In-memory fallback
        if user_id:
            return [s for s in cls._in_memory_sessions.values() if s.get("user_id") == user_id]
        return list(cls._in_memory_sessions.values())

    @classmethod
    async def update_session(cls, session_id: str, state_data: Dict[str, Any]):
        state_data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cls._in_memory_sessions[session_id] = state_data
        await MongoStateCheckpointer.save_session_state(session_id, state_data)


session_service = SessionService()
