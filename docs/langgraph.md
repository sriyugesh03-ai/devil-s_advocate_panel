# 🕸️ LangGraph Multi-Agent State Machine

This document details the **LangGraph** multi-agent state graph, cyclic node orchestration, human-in-the-loop interrupt mechanisms, and state checkpointing utilized by the **Devil's Advocate Panel**.

---

## 🎯 Why LangGraph?

Standard linear LLM chains are insufficient for a realistic multi-round debate. **LangGraph** provides:
1. **Cyclic State Machine**: Enables iterative 3-round interrogations where each round dynamically adapts to founder counter-arguments.
2. **Stateful Graph (`PanelState`)**: Maintains a single source of truth across all 3 agents, rounds, and user responses.
3. **Human-in-the-Loop Interruption (`await_user`)**: Pauses server execution after agents generate questions, persisting state to MongoDB while waiting for founder input.
4. **Resumable Execution**: Allows the session to resume seamlessly when the founder submits their response via HTTP POST.

---

## 🗺️ LangGraph Topology & State Flow

```mermaid
stateDiagram-v2
    [*] --> InitializeState
    InitializeState --> OrchestratorNode: Start Session

    state "Round Execution Subgraph" as RoundExecution {
        OrchestratorNode --> VC_Agent_Node: Invoke Skeptical VC
        VC_Agent_Node --> Financial_Agent_Node: Invoke Financial Analyst
        Financial_Agent_Node --> Market_Agent_Node: Invoke Market Realist
    }

    Market_Agent_Node --> HumanInterrupt: interrupt_before=["await_user"]
    
    state "Human-in-the-Loop Barrier" as HumanInterrupt {
        note right of HumanInterrupt
            Execution pauses.
            State saved to MongoDB.
            Founder answers on web UI.
        end note
    }

    HumanInterrupt --> ResumeExecution: Founder submits /respond
    ResumeExecution --> CheckRoundCondition: Evaluate Defenses

    state CheckRoundCondition <<choice>>
    CheckRoundCondition --> OrchestratorNode: Round < 3 (Increment Round)
    CheckRoundCondition --> VerdictArbiterNode: Round == 3 (Completed)

    VerdictArbiterNode --> GeneratePDFReport: Compute 5-Pillar Score
    GeneratePDFReport --> [*]: Terminate Graph
```

---

## 📦 State Definition (`PanelState`)

The state is defined using strongly-typed schemas in [backend/app/graph/state.py](file:///d:/projects/devil's_advocate_panel/backend/app/graph/state.py):

```python
from typing import TypedDict, List, Dict, Any, Optional

class PanelState(TypedDict):
    session_id: str
    pitch: Dict[str, Any]                 # Title, problem, solution, TAM, business model, traction
    current_round: int                    # 1, 2, or 3
    max_rounds: int                       # Default: 3
    is_completed: bool                    # Set to True after Round 3
    mcp_context: Dict[str, Any]           # Live Tavily, GitHub, and Pitch Deck data
    rag_context: List[str]                # Retrieved failure post-mortems and SaaS comps
    
    # Dialogue History
    round_challenges: Dict[int, Dict[str, str]]   # {1: {"vc": "...", "financial": "...", "market": "..."}}
    founder_responses: Dict[int, str]             # {1: "Founder's defense for Round 1", ...}
    
    # Final Output
    verdict: Optional[Dict[str, Any]]             # Composite score, decision, weakness matrix, roadmap
```

---

## ⚙️ Graph Construction & Node Flow

The graph is compiled in [backend/app/graph/graph.py](file:///d:/projects/devil's_advocate_panel/backend/app/graph/graph.py):

```python
from langgraph.graph import StateGraph, END
from backend.app.graph.state import PanelState
from backend.app.graph.nodes import (
    orchestrator_node,
    vc_agent_node,
    financial_agent_node,
    market_agent_node,
    await_user_node,
    verdict_node
)
from backend.app.graph.edges import should_continue_rounds

def build_panel_graph(checkpointer=None):
    workflow = StateGraph(PanelState)

    # 1. Register Nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("vc_agent", vc_agent_node)
    workflow.add_node("financial_agent", financial_agent_node)
    workflow.add_node("market_agent", market_agent_node)
    workflow.add_node("await_user", await_user_node)
    workflow.add_node("verdict_arbiter", verdict_node)

    # 2. Define Sequential & Parallel Edges
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "vc_agent")
    workflow.add_edge("vc_agent", "financial_agent")
    workflow.add_edge("financial_agent", "market_agent")
    workflow.add_edge("market_agent", "await_user")

    # 3. Define Conditional Routing
    workflow.add_conditional_edges(
        "await_user",
        should_continue_rounds,
        {
            "continue": "orchestrator",
            "verdict": "verdict_arbiter"
        }
    )
    workflow.add_edge("verdict_arbiter", END)

    # 4. Compile with Interruption Trigger
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["await_user"]
    )
```

---

## 💾 State Checkpointing (`MongoStateCheckpointer`)

When the graph hits `interrupt_before=["await_user"]`:
1. The **`MongoStateCheckpointer`** serializes the entire `PanelState` into the `sessions` collection in MongoDB Atlas.
2. The FastAPI controller returns the Round 1 challenges to the Next.js frontend.
3. When the user posts their counter-defense to `POST /api/sessions/{id}/respond`, the checkpointer reloads the state, injects `founder_responses[round] = response`, and calls `graph.invoke(None, config={"configurable": {"thread_id": session_id}})`.
4. Execution resumes smoothly from the exact node where it was paused.
