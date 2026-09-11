import logging
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.mcp.tools import TavilySearchTool, GitHubDiligenceTool, PitchDeckParserTool, get_langchain_mcp_tools
from backend.app.mcp.oauth import mcp_oauth_manager

logger = logging.getLogger(__name__)

class MCPService:
    """Central manager and coordinator for all Model Context Protocol (MCP) integrations."""

    def __init__(self):
        self.tavily = TavilySearchTool()
        self.github = GitHubDiligenceTool()
        self.pitch_deck_parser = PitchDeckParserTool()
        self.oauth_manager = mcp_oauth_manager

    def get_langchain_tools(self) -> List[Any]:
        """Returns LangChain compatible MCP tools."""
        return get_langchain_mcp_tools()

    async def get_connectors_status(self, user_id: str = "default") -> Dict[str, Any]:
        """Returns the real-time operational status of all registered MCP servers, checking both OAuth and environment tokens."""
        has_tavily = bool(settings.TAVILY_API_KEY.strip())
        github_token = self.oauth_manager.get_token(user_id, "github") or settings.GITHUB_PERSONAL_ACCESS_TOKEN.strip()
        has_github = bool(github_token)

        is_oauth_connected = bool(self.oauth_manager.get_token(user_id, "github"))
        has_oauth_app = bool(self.oauth_manager.github_client_id and self.oauth_manager.github_client_secret)
        
        github_status = "connected" if (is_oauth_connected or has_github) else ("ready_to_connect" if has_oauth_app else "unconfigured")
        github_auth_type = "OAuth 2.0 (Connected)" if is_oauth_connected else ("Personal Access Token" if has_github else ("OAuth 2.0 (Configured)" if has_oauth_app else "None"))

        return {
            "total_connectors": 3,
            "active_connectors": (1 if has_tavily else 0) + (1 if has_github else 0) + 1,
            "oauth_status": self.oauth_manager.get_oauth_status(user_id),
            "oauth_app_configured": has_oauth_app,
            "connectors": [
                {
                    "id": "tavily-search",
                    "name": "Live Web & Competitor Search",
                    "provider": "Tavily MCP",
                    "icon": "globe",
                    "status": "connected" if has_tavily else "configured_fallback",
                    "quota": "1,000 requests/mo (Free Tier)",
                    "auth_type": "API Key",
                    "description": "Real-time competitor intelligence, funding database lookups, and market pricing verification.",
                    "capabilities": [
                        "Stealth competitor discovery",
                        "Live pricing page scraping",
                        "Crunchbase & TechCrunch funding checks"
                    ]
                },
                {
                    "id": "github-diligence",
                    "name": "GitHub Technical Diligence",
                    "provider": "GitHub MCP",
                    "icon": "github",
                    "status": github_status,
                    "quota": "5,000 requests/hr (Free Tier)",
                    "auth_type": github_auth_type,
                    "is_oauth_connected": is_oauth_connected,
                    "has_oauth_app": has_oauth_app,
                    "description": "Deep repository inspection, commit velocity tracking, language ratios, and technical moat verification.",
                    "capabilities": [
                        "Commit velocity analysis",
                        "Language & stack ratio breakdown",
                        "Open-source dependency audit"
                    ]
                },
                {
                    "id": "deck-parser",
                    "name": "Pitch Deck & Document Ingestion",
                    "provider": "Filesystem / PDF Parser MCP",
                    "icon": "file-text",
                    "status": "connected",
                    "quota": "Unlimited (Local Engine)",
                    "auth_type": "Native MCP",
                    "description": "Extracts pitch narrative, TAM/SAM numbers, and financial tables directly from uploaded PDF pitch decks.",
                    "capabilities": [
                        "PDF slide text extraction",
                        "Financial model ingestion",
                        "Automatic pitch form population"
                    ]
                }
            ]
        }

    async def search_market_intel(self, pitch_title: str, target_market: str, competition: str) -> str:
        """Executes an automated market intel search for Market Realist & VC agents."""
        query = f"competitors pricing market trends '{pitch_title}' in {target_market} vs {competition}"
        search_res = await self.tavily.search(query, max_results=3)
        if search_res.get("status") == "success":
            results = search_res.get("results", [])
            lines = [f"Live Web Intel for {pitch_title}:"]
            if search_res.get("answer"):
                lines.append(f"Summary: {search_res['answer']}")
            for r in results:
                lines.append(f"- [{r.get('title')}] ({r.get('url')}): {r.get('content')}")
            return "\n".join(lines)
        return ""

    async def audit_github_repository(self, repo_url: str, user_id: str = "default") -> str:
        """Conducts technical diligence on the founder's GitHub repository using user OAuth or configured PAT."""
        if not repo_url or "github.com" not in repo_url:
            return ""
        custom_token = self.oauth_manager.get_token(user_id, "github")
        audit = await self.github.audit_repository(repo_url, custom_token=custom_token)
        if audit.get("status") == "success":
            return (
                f"GitHub Technical Diligence for {audit.get('repo_name')}:\n"
                f"- Primary Language: {audit.get('primary_language')}\n"
                f"- Stars: {audit.get('stars')} | Forks: {audit.get('forks')} | Open Issues: {audit.get('open_issues')}\n"
                f"- Languages Breakdown: {audit.get('languages_breakdown')}\n"
                f"- Recent Commits Count: {audit.get('recent_commit_count')} in latest audit\n"
                f"- Last Pushed: {audit.get('pushed_at')}\n"
                f"- Description: {audit.get('description')}"
            )
        return f"GitHub Audit Notice: {audit.get('message', 'Repository could not be audited.')}"

mcp_service = MCPService()
