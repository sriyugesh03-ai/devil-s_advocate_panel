import json
from typing import Dict, Any, List, Optional
from backend.app.agents.base_agent import BaseSpecialistAgent
from backend.app.schemas.agent import AgentChallenge, AgentReaction, AgentPersona, SeverityLevel
from backend.app.llm.base import BaseLLMAdapter

from backend.app.mcp.service import mcp_service

class SkepticalVCAgent(BaseSpecialistAgent):
    """Skeptical Venture Capitalist persona agent with GitHub Technical Diligence MCP."""

    def __init__(self, llm_service: Optional[BaseLLMAdapter] = None):
        super().__init__(
            persona=AgentPersona.VC,
            prompt_filename="vc.txt",
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
        
        # Ingest GitHub Technical Diligence if repository URL provided
        mcp_github_diligence = ""
        github_url = pitch.get("github_url", "")
        if github_url and "github.com" in github_url:
            try:
                mcp_github_diligence = await mcp_service.audit_github_repository(github_url)
            except Exception:
                pass

        user_prompt = (
            f"=== STARTUP PITCH ===\n"
            f"Title: {pitch.get('title')}\n"
            f"Tagline: {pitch.get('tagline')}\n"
            f"Problem: {pitch.get('problem')}\n"
            f"Solution: {pitch.get('solution')}\n"
            f"Business Model: {pitch.get('business_model')}\n"
            f"Traction: {pitch.get('traction')}\n"
            f"Competition: {pitch.get('competition')}\n\n"
            f"=== CURRENT ROUND ===\n"
            f"Round: {round_number} of 3\n\n"
            f"=== CONVERSATION HISTORY ===\n"
            f"{history_str}\n\n"
            f"=== DOMAIN BENCHMARKS & RAG CONTEXT ===\n"
            f"{rag_context}\n\n"
            f"=== MCP GITHUB CODEBASE DILIGENCE ===\n"
            f"{mcp_github_diligence or 'No GitHub repository submitted.'}\n\n"
            f"Attack the moat, defensibility, codebase authenticity, scalability, and long-term exit viability."
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
            f"Startup: {pitch.get('title')} ({pitch.get('tagline')})\n\n"
            f"=== YOUR PREVIOUS CHALLENGE (Round {round_number}) ===\n"
            f"{agent_question}\n\n"
            f"=== FOUNDER'S RESPONSE ===\n"
            f"{founder_answer}\n\n"
            f"Critique the founder's response. Did they dodge? Did they prove a structural moat? Rate satisfaction 0-100."
        )

        return await self.llm_service.generate_structured(
            prompt=user_prompt,
            response_model=AgentReaction,
            system_instruction=self.prompt_template,
            temperature=0.3,
        )
