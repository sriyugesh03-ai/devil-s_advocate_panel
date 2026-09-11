from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel
from backend.app.mcp.service import mcp_service
from backend.app.mcp.oauth import mcp_oauth_manager

router = APIRouter(prefix="/mcp", tags=["MCP Connectors"])

class OAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None
    user_id: Optional[str] = "default"

class ManualTokenRequest(BaseModel):
    provider: str
    token: str
    user_id: Optional[str] = "default"

@router.get("/status")
async def get_mcp_status(user_id: str = Query("default")):
    """Returns the live status, capabilities, and quotas of all connected MCP servers."""
    try:
        status_data = await mcp_service.get_connectors_status(user_id=user_id)
        return status_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch MCP connectors status: {str(e)}"
        )

@router.get("/oauth/github/authorize")
async def get_github_oauth_url(redirect_uri: str = Query("http://localhost:3000/connectors")):
    """Returns the GitHub OAuth authorization URL for initiating browser login."""
    if not mcp_oauth_manager.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GITHUB_CLIENT_ID is not configured on the backend. Please add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET to your environment variables."
        )
    auth_url = mcp_oauth_manager.get_github_auth_url(redirect_uri=redirect_uri)
    return {"auth_url": auth_url}

@router.post("/oauth/github/callback")
async def handle_github_oauth_callback(payload: OAuthCallbackRequest):
    """Exchanges GitHub OAuth code for access token and saves to user session."""
    res = await mcp_oauth_manager.exchange_github_code(
        code=payload.code,
        redirect_uri=payload.redirect_uri
    )
    if res.get("status") == "success":
        mcp_oauth_manager.store_token(
            user_id=payload.user_id or "default",
            provider="github",
            token=res.get("access_token", ""),
            metadata={"scope": res.get("scope")}
        )
        return {"status": "success", "message": "GitHub MCP OAuth connected successfully."}
    return res

@router.post("/oauth/token")
async def set_manual_oauth_token(payload: ManualTokenRequest):
    """Stores a manual PAT/API Token for a specific MCP connector."""
    mcp_oauth_manager.store_token(
        user_id=payload.user_id or "default",
        provider=payload.provider.lower(),
        token=payload.token.strip()
    )
    return {"status": "success", "message": f"{payload.provider} token configured successfully."}

@router.delete("/oauth/{provider}")
async def disconnect_oauth_provider(provider: str, user_id: str = Query("default")):
    """Disconnects and removes stored OAuth credentials for an MCP provider."""
    removed = mcp_oauth_manager.remove_token(user_id=user_id, provider=provider.lower())
    return {"status": "success", "disconnected": removed}
