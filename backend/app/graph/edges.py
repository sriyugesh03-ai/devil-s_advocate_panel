"""Graph edges and conditional routing helpers."""
from typing import Dict, Any

def should_continue_debate(state: Dict[str, Any]) -> str:
    current_round = state.get("current_round", 1)
    total_rounds = state.get("total_rounds", 3)
    if current_round < total_rounds:
        return "next_round"
    return "final_verdict"
