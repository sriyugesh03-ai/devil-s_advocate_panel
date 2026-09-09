from typing import Literal
from backend.app.graph.state import PanelState

def round_progression_router(state: PanelState) -> Literal["retrieve_context", "final_verdict", "end"]:
    """Routes to the next round of interrogation or to final verdict evaluation."""
    current_round = state.get("current_round", 1)
    total_rounds = state.get("total_rounds", 3)
    status = state.get("status", "")

    if current_round < total_rounds:
        # Advance to next round
        return "retrieve_context"
    else:
        # Final round finished, proceed to synthesize investment verdict
        return "final_verdict"
