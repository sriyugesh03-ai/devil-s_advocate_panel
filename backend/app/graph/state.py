from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class PanelState(TypedDict, total=False):
    # Session identity
    session_id: str
    thread_id: str
    
    # Original validated pitch
    pitch: Dict[str, Any]
    
    # Workflow progress
    current_round: int
    total_rounds: int
    status: str
    
    # Retrieved grounding context per domain/persona
    retrieved_contexts: Dict[str, str]  # keys: "vc", "financial", "market"
    
    # Challenges generated in the current round (merged from parallel branches)
    current_challenges: Annotated[List[Dict[str, Any]], operator.add]
    
    # Founder responses per round
    user_responses: List[Dict[str, Any]]
    
    # Panel reactions to the founder's response in current round
    current_reactions: Annotated[List[Dict[str, Any]], operator.add]
    
    # Full historical transcripts of all rounds
    rounds_history: List[Dict[str, Any]]
    
    # Synthesized final investment verdict
    verdict: Optional[Dict[str, Any]]
    
    # Status & error handling
    error_message: Optional[str]
