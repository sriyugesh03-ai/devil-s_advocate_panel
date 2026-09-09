import pytest
from unittest.mock import AsyncMock, patch
from backend.app.graph.graph import build_panel_graph
from backend.app.schemas.agent import AgentChallenge, AgentPersona, SeverityLevel

@pytest.mark.asyncio
async def test_graph_structure():
    graph = build_panel_graph()
    assert graph is not None
