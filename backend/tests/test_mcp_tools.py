import pytest
from unittest.mock import AsyncMock, patch
from backend.app.mcp.tools import TavilySearchTool, GitHubDiligenceTool, PitchDeckParserTool
from backend.app.mcp.service import mcp_service

@pytest.mark.asyncio
async def test_mcp_connectors_status():
    status = await mcp_service.get_connectors_status()
    assert "connectors" in status
    assert status["total_connectors"] == 3
    assert status["active_connectors"] >= 1

@pytest.mark.asyncio
async def test_tavily_search_mocked():
    tool = TavilySearchTool(api_key="mock_key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json = lambda: {
            "answer": "Market has 5 competitors.",
            "results": [{"title": "Competitor A", "url": "https://a.com", "content": "Tool A"}]
        }
        res = await tool.search("test query")
        assert res["status"] == "success"
        assert len(res["results"]) == 1

@pytest.mark.asyncio
async def test_github_audit_mocked():
    tool = GitHubDiligenceTool(token="mock_token")
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        def side_effect(url, **kwargs):
            mock_res = AsyncMock()
            mock_res.status_code = 200
            if "languages" in url:
                mock_res.json = lambda: {"TypeScript": 1000}
            elif "commits" in url:
                mock_res.json = lambda: [{"commit": {"message": "feat: init", "author": {"date": "2024-01-01"}}}]
            else:
                mock_res.json = lambda: {
                    "description": "Test Repo",
                    "stargazers_count": 50,
                    "forks_count": 5,
                    "open_issues_count": 2,
                    "language": "TypeScript",
                    "created_at": "2024-01-01",
                    "pushed_at": "2024-02-01"
                }
            return mock_res

        mock_get.side_effect = side_effect
        res = await tool.audit_repository("https://github.com/myorg/myrepo")
        assert res["status"] == "success"
        assert res["repo_name"] == "myorg/myrepo"
        assert res["stars"] == 50
        assert len(res["latest_commits"]) == 1
