import os
import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def setup_langsmith_tracing():
    """Configures LangSmith environment tracing variables."""
    if settings.LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info(f"LangSmith tracing enabled for project '{settings.LANGSMITH_PROJECT}'")
    else:
        logger.info("LangSmith API key not configured; tracing is disabled.")

def get_trace_metadata(session_id: str, round_num: int, persona: Optional[str] = None) -> Dict[str, Any]:
    """Standardized metadata dictionary for LangSmith run traces."""
    meta = {
        "session_id": session_id,
        "round_number": round_num,
        "app": "devils_advocate_panel",
        "env": settings.ENVIRONMENT,
    }
    if persona:
        meta["persona"] = persona
    return meta
