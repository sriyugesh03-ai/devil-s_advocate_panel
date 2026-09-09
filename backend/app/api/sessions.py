from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.session import UserResponseSubmit
from backend.app.services.session_service import session_service
from backend.app.services.debate_service import debate_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("/{session_id}")
async def get_session_state(session_id: str):
    """Fetches the current live state of a panel session."""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )
    return session

@router.post("/{session_id}/response")
async def submit_response(session_id: str, payload: UserResponseSubmit):
    """Submits the founder's answer to the current round challenges, advancing the gauntlet."""
    if payload.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID in URL path does not match request body."
        )

    try:
        updated_session = await debate_service.submit_and_advance_round(
            session_id=session_id,
            round_number=payload.round_number,
            founder_response=payload.response_text,
        )
        return updated_session
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate response and advance round: {str(e)}"
        )

@router.get("/{session_id}/transcript")
async def get_session_transcript(session_id: str):
    """Fetches complete round transcript history for a session."""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )
    return {
        "session_id": session_id,
        "pitch": session.get("pitch"),
        "rounds_history": session.get("rounds_history", [])
    }
