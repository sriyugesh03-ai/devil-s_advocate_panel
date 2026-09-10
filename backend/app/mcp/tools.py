import logging
import re
import io
from typing import Dict, Any, List, Optional
import httpx
from pypdf import PdfReader
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

    async def audit_repository(self, repo_url: str) -> Dict[str, Any]:
        parsed = self._extract_owner_repo(repo_url)
        if not parsed:
            return {"status": "error", "message": "Invalid GitHub repository URL format."}

        owner, repo = parsed
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Devils-Advocate-Panel-MCP"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

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
            for i, page in enumerate(reader.pages[:25]):  # limit to first 25 slides
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
            "Extract structured startup pitch information from the provided pitch deck slides."
        )
        prompt = (
            f"=== PITCH DECK SLIDE CONTENTS ===\n"
            f"{deck_text[:12000]}\n\n"
            f"Extract and format the startup pitch into the required structured JSON format."
        )
        return await self.llm.generate_structured(
            prompt=prompt,
            response_model=StartupPitchCreate,
            system_instruction=system_prompt,
            temperature=0.2
        )
