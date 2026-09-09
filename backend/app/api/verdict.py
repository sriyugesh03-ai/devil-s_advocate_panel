from fastapi import APIRouter, HTTPException, status
from backend.app.services.verdict_service import verdict_service

router = APIRouter(prefix="/verdict", tags=["Verdict"])

@router.get("/{session_id}")
async def get_or_generate_verdict(session_id: str):
    """Generates or fetches the final investment diagnostic verdict report for a session."""
    try:
        verdict = await verdict_service.generate_verdict_for_session(session_id)
        return verdict
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate final verdict: {str(e)}"
        )
