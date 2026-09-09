import logging
from typing import Callable, Any, TypeVar
import asyncio
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
T = TypeVar("T")

class PanelException(Exception):
    """Base exception for Devil's Advocate Panel domain errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class LLMProviderError(PanelException):
    """Raised when LLM provider returns an error, times out, or rate limits."""
    def __init__(self, message: str = "LLM provider temporarily unavailable."):
        super().__init__(message, status_code=503)

class SessionNotFoundError(PanelException):
    """Raised when the requested session ID is not found."""
    def __init__(self, session_id: str):
        super().__init__(f"Session '{session_id}' not found.", status_code=404)

async def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Any:
    """Executes an async function with exponential backoff retry on failure."""
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}. Retrying in {delay:.2f}s...")
            if attempt == max_retries:
                break
            await asyncio.sleep(delay)
            delay *= backoff_factor

    logger.error(f"All {max_retries} retry attempts failed.")
    raise last_exception or LLMProviderError()

async def panel_exception_handler(request: Request, exc: PanelException):
    """FastAPI global exception handler for domain errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )
