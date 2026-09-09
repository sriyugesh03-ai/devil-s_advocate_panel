from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from backend.app.services.session_service import session_service
from backend.app.services.verdict_service import verdict_service
from backend.app.pdf.generator import pdf_generator

router = APIRouter(prefix="/pdf", tags=["PDF"])

@router.get("/{session_id}/download")
async def download_pdf_report(session_id: str):
    """Generates and streams a downloadable PDF investment diagnostic report."""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    # Ensure verdict is generated
    if not session.get("verdict"):
        try:
            verdict = await verdict_service.generate_verdict_for_session(session_id)
            session["verdict"] = verdict.model_dump()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not generate verdict for PDF: {e}"
            )

    try:
        pdf_buffer = pdf_generator.generate_report(session)
        pitch_title = session.get("pitch", {}).get("title", "pitch").replace(" ", "_")
        filename = f"Devils_Advocate_Report_{pitch_title}_{session_id}.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render PDF: {str(e)}"
        )
