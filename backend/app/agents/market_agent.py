import json
from typing import Dict, Any, List, Optional
from backend.app.agents.base_agent import BaseSpecialistAgent
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.llm.base import BaseLLMAdapter

from backend.app.mcp.service import mcp_service

class MarketRealistAgent(BaseSpecialistAgent):
    """Market Realist persona agent with MCP Live Web Intelligence."""

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
        history_str = json.dumps(conversation_history, indent=2, default=str) if conversation_history else "Round 1 (Initial Pitch)"
        
        # Ingest Live MCP Competitor Intelligence
        mcp_live_intel = ""
        try:
            mcp_live_intel = await mcp_service.search_market_intel(
                pitch.get("title", ""),
                pitch.get("target_market", ""),
                pitch.get("competition", "")
            )
        except Exception:
            pass

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
            f"=== DOMAIN BENCHMARKS & RAG CONTEXT ===\n"
            f"{rag_context}\n\n"
            f"=== MCP LIVE WEB & COMPETITOR INTEL ===\n"
            f"{mcp_live_intel or 'No live web intel available.'}\n\n"
            f"Expose incumbent bundling risks, buyer inertia, distribution bottlenecks, real-world competing alternatives, and market timing flaws."
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
