from langgraph.graph import StateGraph, START, END
from backend.app.graph.state import PanelState
from backend.app.graph.nodes import (
    analyze_pitch_node,
    retrieve_context_node,
    vc_agent_node,
    financial_agent_node,
    market_agent_node,
    merge_challenges_node,
    evaluate_reactions_node,
)
from backend.app.graph.router import round_progression_router
from backend.app.graph.checkpointer import memory_checkpointer

def build_panel_graph():
    """Builds and compiles the multi-agent Devil's Advocate StateGraph."""
    workflow = StateGraph(PanelState)

    # Add Nodes
    workflow.add_node("analyze_pitch", analyze_pitch_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    
    # 3 Specialist parallel nodes
    workflow.add_node("vc_agent", vc_agent_node)
    workflow.add_node("financial_agent", financial_agent_node)
    workflow.add_node("market_agent", market_agent_node)
    
    workflow.add_node("merge_challenges", merge_challenges_node)
    workflow.add_node("evaluate_reactions", evaluate_reactions_node)

    # Define Edges
    workflow.add_edge(START, "analyze_pitch")
    workflow.add_edge("analyze_pitch", "retrieve_context")
    
    # Fan-out to 3 specialist agents in parallel
    workflow.add_edge("retrieve_context", "vc_agent")
    workflow.add_edge("retrieve_context", "financial_agent")
    workflow.add_edge("retrieve_context", "market_agent")
    
    # Fan-in from 3 specialist agents to merge node
    workflow.add_edge("vc_agent", "merge_challenges")
    workflow.add_edge("financial_agent", "merge_challenges")
    workflow.add_edge("market_agent", "merge_challenges")

    # The graph pauses after merge_challenges for user input (Human-In-The-Loop)
    workflow.add_edge("merge_challenges", END)

    # After human response is injected:
    workflow.add_edge("evaluate_reactions", END)

    return workflow.compile(checkpointer=memory_checkpointer)

panel_graph = build_panel_graph()
