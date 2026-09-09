import asyncio
import logging
from typing import Dict, Any, List
from backend.app.graph.state import PanelState
from backend.app.rag.service import rag_service
from backend.app.agents.vc_agent import SkepticalVCAgent
from backend.app.agents.financial_agent import FinancialAnalystAgent
from backend.app.agents.market_agent import MarketRealistAgent

logger = logging.getLogger(__name__)

vc_agent = SkepticalVCAgent()
financial_agent = FinancialAnalystAgent()
market_agent = MarketRealistAgent()

async def analyze_pitch_node(state: PanelState) -> Dict[str, Any]:
    """Validates pitch and initializes session round state."""
    logger.info(f"Analyzing pitch for session {state.get('session_id')}")
    current_round = state.get("current_round", 1)
    return {
        "current_round": current_round,
        "total_rounds": state.get("total_rounds", 3),
        "status": "pitch_analyzed",
        "current_challenges": [],
        "current_reactions": [],
    }

async def retrieve_context_node(state: PanelState) -> Dict[str, Any]:
    """Retrieves domain benchmarks and context for all 3 agents via RAG."""
    pitch = state.get("pitch", {})
    logger.info(f"Retrieving domain context for pitch: {pitch.get('title')}")
    contexts = await rag_service.get_contexts_for_pitch(pitch)
    return {
        "retrieved_contexts": contexts,
        "status": "context_retrieved",
    }

async def vc_agent_node(state: PanelState) -> Dict[str, Any]:
    """Generates challenge from the Skeptical VC."""
    pitch = state.get("pitch", {})
    round_num = state.get("current_round", 1)
    rag_ctx = state.get("retrieved_contexts", {}).get("vc", "")
    history = state.get("rounds_history", [])

    challenge = await vc_agent.generate_challenge(
        pitch=pitch,
        round_number=round_num,
        rag_context=rag_ctx,
        conversation_history=history,
    )
    return {"current_challenges": [challenge.model_dump()]}

async def financial_agent_node(state: PanelState) -> Dict[str, Any]:
    """Generates challenge from the Financial Analyst."""
    pitch = state.get("pitch", {})
    round_num = state.get("current_round", 1)
    rag_ctx = state.get("retrieved_contexts", {}).get("financial", "")
    history = state.get("rounds_history", [])

    challenge = await financial_agent.generate_challenge(
        pitch=pitch,
        round_number=round_num,
        rag_context=rag_ctx,
        conversation_history=history,
    )
    return {"current_challenges": [challenge.model_dump()]}

async def market_agent_node(state: PanelState) -> Dict[str, Any]:
    """Generates challenge from the Market Realist."""
    pitch = state.get("pitch", {})
    round_num = state.get("current_round", 1)
    rag_ctx = state.get("retrieved_contexts", {}).get("market", "")
    history = state.get("rounds_history", [])

    challenge = await market_agent.generate_challenge(
        pitch=pitch,
        round_number=round_num,
        rag_context=rag_ctx,
        conversation_history=history,
    )
    return {"current_challenges": [challenge.model_dump()]}

async def merge_challenges_node(state: PanelState) -> Dict[str, Any]:
    """Consolidates challenges from all specialist agents and pauses for human response."""
    challenges = state.get("current_challenges", [])
    logger.info(f"Consolidated {len(challenges)} challenges for Round {state.get('current_round')}")
    return {
        "status": "awaiting_user_response",
    }

async def evaluate_reactions_node(state: PanelState) -> Dict[str, Any]:
    """Generates individual agent reactions to the founder's defense."""
    pitch = state.get("pitch", {})
    round_num = state.get("current_round", 1)
    challenges = state.get("current_challenges", [])
    user_responses = state.get("user_responses", [])
    
    # Get latest founder response
    founder_answer = user_responses[-1].get("response_text", "") if user_responses else ""

    # Run reactions in parallel
    reaction_tasks = []
    for ch in challenges:
        persona = ch.get("persona")
        q = ch.get("question", "")
        if "VC" in persona:
            reaction_tasks.append(vc_agent.generate_reaction(pitch, round_num, q, founder_answer))
        elif "Financial" in persona:
            reaction_tasks.append(financial_agent.generate_reaction(pitch, round_num, q, founder_answer))
        elif "Market" in persona:
            reaction_tasks.append(market_agent.generate_reaction(pitch, round_num, q, founder_answer))

    reactions = await asyncio.gather(*reaction_tasks, return_exceptions=True)
    valid_reactions = [r.model_dump() for r in reactions if hasattr(r, "model_dump")]

    # Archive this round into rounds_history
    current_round_record = {
        "round_number": round_num,
        "challenges": challenges,
        "founder_response": founder_answer,
        "reactions": valid_reactions,
    }
    updated_history = list(state.get("rounds_history", []))
    updated_history.append(current_round_record)

    return {
        "current_reactions": valid_reactions,
        "rounds_history": updated_history,
        "current_challenges": [],  # reset for next round
        "status": "round_evaluated",
    }
