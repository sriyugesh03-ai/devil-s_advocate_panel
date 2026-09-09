import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.llm.factory import get_llm_service

logger = logging.getLogger(__name__)

class BaseSpecialistAgent(ABC):
    """Base class for specialist investor personas."""

    def __init__(self, persona: AgentPersona, prompt_filename: str, llm_service: Optional[BaseLLMAdapter] = None):
        self.persona = persona
        self.llm_service = llm_service or get_llm_service()
        self.prompt_template = self._load_prompt(prompt_filename)

    def _load_prompt(self, filename: str) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", filename)
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Could not load prompt from {prompt_path}: {e}")
            return f"You are the {self.persona.value} on the Devil's Advocate Panel. Challenge the startup ruthlessly."

    @abstractmethod
    async def generate_challenge(
        self,
        pitch: Dict[str, Any],
        round_number: int,
        rag_context: str,
        conversation_history: List[Dict[str, Any]],
    ) -> AgentChallenge:
        """Generate round-specific challenge question and reasoning summary."""
        pass

    @abstractmethod
    async def generate_reaction(
        self,
        pitch: Dict[str, Any],
        round_number: int,
        agent_question: str,
        founder_answer: str,
    ) -> AgentReaction:
        """Generate reaction and critique to the founder's response."""
        pass
