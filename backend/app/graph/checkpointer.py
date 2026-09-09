import logging
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver
from backend.app.db.mongo import get_db

logger = logging.getLogger(__name__)

# In-memory checkpointer for LangGraph runtime loops
memory_checkpointer = MemorySaver()

class MongoStateCheckpointer:
    """Synchronizes state checkpoints to MongoDB collection."""

    @staticmethod
    async def save_session_state(session_id: str, state_data: Dict[str, Any]):
        db = get_db()
        if db is None:
            return
        try:
            await db.sessions.update_one(
                {"session_id": session_id},
                {"$set": state_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error persisting session state to MongoDB: {e}")

    @staticmethod
    async def get_session_state(session_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        if db is None:
            return None
        try:
            return await db.sessions.find_one({"session_id": session_id}, {"_id": 0})
        except Exception as e:
            logger.error(f"Error fetching session state from MongoDB: {e}")
            return None
