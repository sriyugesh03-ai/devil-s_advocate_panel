import logging
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.mcp.tools import TavilySearchTool, GitHubDiligenceTool, PitchDeckParserTool

logger = logging.getLogger(__name__)

class MCPService:
    """Central manager and coordinator for all Model Context Protocol (MCP) integrations."""

    def __init__(self):
        self.tavily = TavilySearchTool()
        self.github = GitHubDiligenceTool()
        self.pitch_deck_parser = PitchDeckParserTool()

    async def get_connectors_status(self) -> Dict[str, Any]:
        """Returns the real-time operational status of all registered MCP servers."""
        has_tavily = bool(settings.TAVILY_API_KEY.strip())
        has_github = bool(settings.GITHUB_PERSONAL_ACCESS_TOKEN.strip())

        return {
            "total_connectors": 3,
            "active_connectors": (1 if has_tavily else 0) + (1 if has_github else 0) + 1,
            "connectors": [
                {
                    "id": "tavily-search",
                    "name": "Live Web & Competitor Search",
                    "provider": "Tavily MCP",
                    "icon": "globe",
                    "status": "connected" if has_tavily else "configured_fallback",
                    "quota": "1,000 requests/mo (Free Tier)",
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
                    "status": "connected" if has_github else "unconfigured",
                    "quota": "5,000 requests/hr (Free Tier)",
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

    async def audit_github_repository(self, repo_url: str) -> str:
        """Conducts technical diligence on the founder's GitHub repository."""
        if not repo_url or "github.com" not in repo_url:
            return ""
        audit = await self.github.audit_repository(repo_url)
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
