import logging
import re
import io
from typing import Dict, Any, List, Optional
import httpx
from pypdf import PdfReader
from langchain_core.tools import tool, StructuredTool
from backend.app.core.config import settings
from backend.app.llm.factory import get_llm_service
from backend.app.schemas.pitch import StartupPitchCreate

logger = logging.getLogger(__name__)

class TavilySearchTool:
    """MCP Tool: Live Web & Competitor Search via Tavily."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or settings.TAVILY_API_KEY).strip()
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 4) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "results": [],
                "summary": "Tavily API key not configured; live search bypassed."
            }

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": max_results
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(self.base_url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    raw_results = data.get("results", [])
                    formatted = [
                        {
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "content": r.get("content")[:280]
                        }
                        for r in raw_results
                    ]
                    return {
                        "status": "success",
                        "answer": answer,
                        "results": formatted,
                        "query": query
                    }
                else:
                    logger.warning(f"Tavily search returned status {res.status_code}: {res.text[:120]}")
                    return {"status": "error", "results": [], "summary": f"Search failed with HTTP {res.status_code}"}
        except Exception as e:
            logger.warning(f"Tavily search execution error: {e}")
            return {"status": "error", "results": [], "summary": str(e)}


class GitHubDiligenceTool:
    """MCP Tool: Technical Codebase Diligence via GitHub API."""

    def __init__(self, token: Optional[str] = None):
        self.token = (token or settings.GITHUB_PERSONAL_ACCESS_TOKEN).strip()
        self.base_url = "https://api.github.com"

    def _extract_owner_repo(self, repo_url: str) -> Optional[tuple]:
        match = re.search(r"github\.com/([^/]+)/([^/\s#?]+)", repo_url)
        if match:
            owner = match.group(1).strip()
            repo = match.group(2).strip()
            if repo.endswith(".git"):
                repo = repo[:-4]
            return owner, repo
        return None

    async def audit_repository(self, repo_url: str, custom_token: Optional[str] = None) -> Dict[str, Any]:
        parsed = self._extract_owner_repo(repo_url)
        if not parsed:
            return {"status": "error", "message": "Invalid GitHub repository URL format."}

        owner, repo = parsed
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Devils-Advocate-Panel-MCP"
        }
        token_to_use = (custom_token or self.token or "").strip()
        if token_to_use:
            headers["Authorization"] = f"Bearer {token_to_use}"

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                # 1. Fetch Repo Metadata
                repo_res = await client.get(f"{self.base_url}/repos/{owner}/{repo}", headers=headers)
                if repo_res.status_code != 200:
                    return {
                        "status": "error",
                        "message": f"Could not access GitHub repo {owner}/{repo} (HTTP {repo_res.status_code})"
                    }
                repo_data = repo_res.json()

                # 2. Fetch Languages Breakdown
                lang_res = await client.get(f"{self.base_url}/repos/{owner}/{repo}/languages", headers=headers)
                languages = lang_res.json() if lang_res.status_code == 200 else {}

                # 3. Fetch Recent Commits (Commit Velocity)
                commits_res = await client.get(f"{self.base_url}/repos/{owner}/{repo}/commits?per_page=5", headers=headers)
                recent_commits = []
                if commits_res.status_code == 200:
                    commits_data = commits_res.json()
                    if isinstance(commits_data, list):
                        recent_commits = [
                            {
                                "message": c.get("commit", {}).get("message", "")[:80] if isinstance(c, dict) else "",
                                "date": c.get("commit", {}).get("author", {}).get("date", "") if isinstance(c, dict) else ""
                            }
                            for c in commits_data if isinstance(c, dict)
                        ]

                return {
                    "status": "success",
                    "repo_name": f"{owner}/{repo}",
                    "description": repo_data.get("description", "No description provided"),
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                    "open_issues": repo_data.get("open_issues_count", 0),
                    "primary_language": repo_data.get("language", "Unknown"),
                    "languages_breakdown": languages,
                    "recent_commit_count": len(recent_commits),
                    "latest_commits": recent_commits,
                    "created_at": repo_data.get("created_at"),
                    "pushed_at": repo_data.get("pushed_at"),
                    "is_fork": repo_data.get("fork", False)
                }
        except Exception as e:
            logger.warning(f"GitHub MCP audit error: {e}")
            return {"status": "error", "message": str(e)}


class PitchDeckParserTool:
    """MCP Tool: Pitch Deck Document Ingestion and Field Extraction."""

    def __init__(self):
        self.llm = get_llm_service()

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_pages = []
            for i, page in enumerate(reader.pages[:30]):  # up to 30 slides
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_pages.append(f"--- Slide {i+1} ---\n{page_text.strip()}")
            return "\n\n".join(text_pages)
        except Exception as e:
            logger.error(f"Error extracting text from PDF deck: {e}")
            return ""

    async def parse_deck_into_pitch(self, deck_text: str) -> StartupPitchCreate:
        system_prompt = (
            "You are an expert venture capitalist associate. "
            "Analyze and extract structured startup pitch information from the provided pitch deck slides.\n"
            "Guidelines for extraction:\n"
            "- title: Startup / Company / Project Name (short string)\n"
            "- tagline: High-impact one-liner explaining what it does\n"
            "- problem: Clear summary of customer pain points addressed in the deck\n"
            "- solution: How the product/technology uniquely solves the problem\n"
            "- target_market: Target customers, market segment, and TAM/SAM estimates\n"
            "- business_model: Monetization approach, pricing structure, and revenue drivers\n"
            "- traction: Current traction, pilots, metrics, users, or roadmap stage\n"
            "- competition: Key competitors or alternative solutions mentioned or implied\n"
            "- fundraising_goal: Amount seeking to raise and use of funds (concise summary)\n"
            "If any field is not explicitly mentioned in the slides, make a concise, realistic inference based on the deck contents."
        )
        prompt = (
            f"=== PITCH DECK SLIDE CONTENTS ===\n"
            f"{deck_text[:14000]}\n\n"
            f"Extract and format the pitch into valid JSON format."
        )

        try:
            return await self.llm.generate_structured(
                prompt=prompt,
                response_model=StartupPitchCreate,
                system_instruction=system_prompt,
                temperature=0.2
            )
        except Exception as e:
            logger.warning(f"Structured deck parsing encountered: {e}. Executing text fallback...")
            try:
                raw_json = await self.llm.generate_text(
                    prompt=prompt + "\n\nCRITICAL: Return ONLY valid JSON with fields: title, tagline, problem, solution, target_market, business_model, traction, competition, fundraising_goal.",
                    system_instruction=system_prompt,
                    temperature=0.2
                )
                # Clean and parse JSON
                cleaned = raw_json.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                match = re.search(r"(\{.*\})", cleaned.strip(), re.DOTALL)
                if match:
                    import json
                    parsed_dict = json.loads(match.group(1))
                    return StartupPitchCreate(**parsed_dict)
            except Exception as fallback_err:
                logger.error(f"Fallback parsing also encountered error: {fallback_err}")

            # Return a graceful basic pitch so user can review and edit in UI
            return StartupPitchCreate(
                title="Extracted Startup Pitch",
                tagline="Pitch extracted from uploaded deck",
                problem=deck_text[:500] if deck_text else "Identified market problem from uploaded deck.",
                solution="Unique technical solution proposed in deck.",
                target_market="Target market segment outlined in deck.",
                business_model="Commercial model outlined in deck."
            )



# ==========================================
# LangChain MCP Tool Adapters
# ==========================================

_tavily_instance = TavilySearchTool()
_github_instance = GitHubDiligenceTool()

@tool
async def tavily_market_search(query: str) -> str:
    """Searches live web intelligence and competitor pricing via Tavily MCP."""
    res = await _tavily_instance.search(query, max_results=3)
    if res.get("status") == "success":
        results = res.get("results", [])
        return "\n".join([f"- [{r.get('title')}] {r.get('content')}" for r in results])
    return "No web intelligence found or tool unconfigured."

@tool
async def github_repo_audit(repo_url: str) -> str:
    """Conducts technical code diligence on a founder's GitHub repository via GitHub MCP."""
    res = await _github_instance.audit_repository(repo_url)
    if res.get("status") == "success":
        return f"Repo: {res.get('repo_name')} | Language: {res.get('primary_language')} | Stars: {res.get('stars')} | Commits in audit: {res.get('recent_commit_count')}"
    return res.get("message", "GitHub audit failed.")

def get_langchain_mcp_tools() -> List[Any]:
    """Returns the list of LangChain MCP tools for agent tool binding."""
    return [tavily_market_search, github_repo_audit]
