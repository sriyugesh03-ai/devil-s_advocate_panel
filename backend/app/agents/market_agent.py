import json
from typing import Dict, Any, List, Optional
from backend.app.agents.base_agent import BaseSpecialistAgent
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.llm.base import BaseLLMAdapter

class MarketRealistAgent(BaseSpecialistAgent):
    """Market Realist persona agent."""

    def __init__(self, llm_service: Optional[BaseLLMAdapter] = None):
        super().__init__(
            persona=AgentPersona.MARKET,
            prompt_filename="market.txt",
            llm_service=llm_service
        )

    async def generate_challenge(
        self,
        pitch: Dict[str, Any],
        round_number: int,
        rag_context: str,
        conversation_history: List[Dict[str, Any]],
    ) -> AgentChallenge:
        history_str = json.dumps(conversation_history, indent=2) if conversation_history else "Round 1 (Initial Pitch)"
        
        user_prompt = (
            f"=== STARTUP PITCH ===\n"
            f"Title: {pitch.get('title')}\n"
            f"Target Market & ICP: {pitch.get('target_market')}\n"
            f"Competition: {pitch.get('competition')}\n"
            f"Solution: {pitch.get('solution')}\n\n"
            f"=== CURRENT ROUND ===\n"
            f"Round: {round_number} of 3\n\n"
            f"=== CONVERSATION HISTORY ===\n"
            f"{history_str}\n\n"
            f"=== MARKET DYNAMICS & RAG CONTEXT ===\n"
            f"{rag_context}\n\n"
            f"Expose incumbent bundling risks, buyer inertia, distribution bottlenecks, and market timing flaws."
        )

        return await self.llm_service.generate_structured(
            prompt=user_prompt,
            response_model=AgentChallenge,
            system_instruction=self.prompt_template,
            temperature=0.4,
        )

    async def generate_reaction(
        self,
        pitch: Dict[str, Any],
        round_number: int,
        agent_question: str,
        founder_answer: str,
    ) -> AgentReaction:
        user_prompt = (
            f"=== PITCH ===\n"
            f"Startup: {pitch.get('title')} | Market: {pitch.get('target_market')}\n\n"
            f"=== YOUR MARKET QUESTION (Round {round_number}) ===\n"
            f"{agent_question}\n\n"
            f"=== FOUNDER'S RESPONSE ===\n"
            f"{founder_answer}\n\n"
            f"Critique their distribution strategy and defense against incumbents. Rate satisfaction 0-100."
        )

        return await self.llm_service.generate_structured(
            prompt=user_prompt,
            response_model=AgentReaction,
            system_instruction=self.prompt_template,
            temperature=0.3,
        )
