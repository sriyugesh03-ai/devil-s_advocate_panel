from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from backend.app.schemas.pitch import StartupPitchCreate
from backend.app.services.session_service import session_service
from backend.app.core.auth import get_optional_user, AuthenticatedUser
from backend.app.mcp.service import mcp_service

router = APIRouter(prefix="/pitches", tags=["Pitches"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_pitch(
    pitch_in: StartupPitchCreate,
    user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Submits a new startup pitch and immediately initializes Round 1 interrogation."""
    try:
        user_id = user.user_id if user else None
        user_email = user.email if user else None
        session_state = await session_service.create_session(
            pitch_data=pitch_in.model_dump(),
            user_id=user_id,
            user_email=user_email
        )
        return session_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process pitch and initialize panel: {str(e)}"
        )

@router.post("/parse-deck")
async def parse_pitch_deck(file: UploadFile = File(...)):
    """Ingests a PDF pitch deck via MCP parser tool and auto-extracts structured pitch fields."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf pitch deck files are supported."
        )

    try:
        contents = await file.read()
        extracted_text = mcp_service.pitch_deck_parser.extract_text_from_pdf(contents)
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract readable text from the uploaded PDF deck."
            )

        structured_pitch = await mcp_service.pitch_deck_parser.parse_deck_into_pitch(extracted_text)
        pitch_dict = structured_pitch.model_dump()
        pitch_dict["pitch_deck_filename"] = file.filename
        return pitch_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse pitch deck: {str(e)}"
        )


