"""Multi-Round Router for Devil's Advocate Debate Engine."""
from typing import Dict, Any, Literal

def determine_round_action(current_round: int, total_rounds: int = 3) -> Literal["continue_debate", "synthesize_verdict"]:
    if current_round < total_rounds:
        return "continue_debate"
    return "synthesize_verdict"
