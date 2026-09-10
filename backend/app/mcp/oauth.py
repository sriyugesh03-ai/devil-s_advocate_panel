import logging
import httpx
from typing import Optional, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory storage for user OAuth tokens (keyed by user_id or session_id / 'default')
_OAUTH_TOKENS: Dict[str, Dict[str, Any]] = {}

class MCPOAuthManager:
    """Manages OAuth 2.0 flows for external MCP services like GitHub and Google."""

    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

    def __init__(self):
        self.github_client_id = getattr(settings, "GITHUB_CLIENT_ID", "").strip()
        self.github_client_secret = getattr(settings, "GITHUB_CLIENT_SECRET", "").strip()

    def get_github_auth_url(self, redirect_uri: str, state: str = "mcp_github_auth") -> str:
        """Constructs the GitHub OAuth authorization URL."""
        client_id = self.github_client_id or "github_mcp_client"
        scope = "repo,read:user,read:org"
        return (
            f"{self.GITHUB_AUTH_URL}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"state={state}"
        )

    async def exchange_github_code(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """Exchanges an authorization code for a GitHub access token."""
        if not self.github_client_id or not self.github_client_secret:
            # If OAuth app credentials are not set in .env, simulate or return guidance
            logger.info("GitHub OAuth client credentials not set, using personal access token mode.")
            return {
                "status": "unconfigured_oauth_app",
                "message": "GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set in .env for live OAuth redirect. Using PAT fallback."
            }

        payload = {
            "client_id": self.github_client_id,
            "client_secret": self.github_client_secret,
            "code": code,
        }
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        headers = {"Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.GITHUB_TOKEN_URL, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    access_token = data.get("access_token")
                    if access_token:
                        return {
                            "status": "success",
                            "access_token": access_token,
                            "token_type": data.get("token_type", "bearer"),
                            "scope": data.get("scope", "")
                        }
                    return {"status": "error", "message": data.get("error_description", "Token exchange failed.")}
                return {"status": "error", "message": f"GitHub token endpoint returned HTTP {res.status_code}"}
        except Exception as e:
            logger.error(f"Error during GitHub OAuth code exchange: {e}")
            return {"status": "error", "message": str(e)}

    def store_token(self, user_id: str, provider: str, token: str, metadata: Optional[Dict[str, Any]] = None):
        """Stores user OAuth token in memory / session store."""
        key = f"{user_id}:{provider}"
        _OAUTH_TOKENS[key] = {
            "token": token,
            "provider": provider,
            "metadata": metadata or {}
        }
        logger.info(f"Stored OAuth token for {key}")

    def get_token(self, user_id: str, provider: str) -> Optional[str]:
        """Retrieves stored OAuth token for user and provider."""
        key = f"{user_id}:{provider}"
        if key in _OAUTH_TOKENS:
            return _OAUTH_TOKENS[key].get("token")
        # Fallback to default user
        default_key = f"default:{provider}"
        if default_key in _OAUTH_TOKENS:
            return _OAUTH_TOKENS[default_key].get("token")
        return None

    def remove_token(self, user_id: str, provider: str) -> bool:
        """Removes an OAuth token for user."""
        key = f"{user_id}:{provider}"
        if key in _OAUTH_TOKENS:
            del _OAUTH_TOKENS[key]
            return True
        return False

    def get_oauth_status(self, user_id: str = "default") -> Dict[str, Any]:
        """Returns OAuth connection status for all supported MCP providers."""
        github_connected = bool(
            self.get_token(user_id, "github") or 
            bool(settings.GITHUB_PERSONAL_ACCESS_TOKEN.strip())
        )
        return {
            "github": {
                "connected": github_connected,
                "auth_type": "oauth" if bool(self.get_token(user_id, "github")) else ("pat" if bool(settings.GITHUB_PERSONAL_ACCESS_TOKEN.strip()) else "none"),
                "provider": "GitHub MCP"
            },
            "tavily": {
                "connected": bool(settings.TAVILY_API_KEY.strip()),
                "auth_type": "api_key" if bool(settings.TAVILY_API_KEY.strip()) else "none",
                "provider": "Tavily MCP"
            }
        }

mcp_oauth_manager = MCPOAuthManager()
