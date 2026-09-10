from fastapi import APIRouter, HTTPException, status
from backend.app.mcp.service import mcp_service

router = APIRouter(prefix="/mcp", tags=["MCP Connectors"])

@router.get("/status")
async def get_mcp_status():
    """Returns the live status, capabilities, and quotas of all connected MCP servers."""
    try:
        status_data = await mcp_service.get_connectors_status()
        return status_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch MCP connectors status: {str(e)}"
        )
