from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.pitch import StartupPitchCreate
from backend.app.services.session_service import session_service

router = APIRouter(prefix="/pitches", tags=["Pitches"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_pitch(pitch_in: StartupPitchCreate):
    """Submits a new startup pitch and immediately initializes Round 1 interrogation."""
    try:
        session_state = await session_service.create_session(pitch_in.model_dump())
        return session_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process pitch and initialize panel: {str(e)}"
        )
