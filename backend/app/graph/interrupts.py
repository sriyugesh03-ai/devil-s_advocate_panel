import uuid
from typing import Dict, Any, Optional

def generate_session_id() -> str:
    """Generates a cryptographically random stable session identifier."""
    return f"sess_{uuid.uuid4().hex[:12]}"

def generate_thread_id(session_id: str) -> str:
    """Generates thread identifier tied to the session for LangGraph checkpointers."""
    return f"th_{session_id}"
