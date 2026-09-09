import logging
from typing import Optional
from backend.app.llm.base import BaseLLMAdapter
from backend.app.llm.gemini import GeminiAdapter
from backend.app.llm.groq import GroqAdapter
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory for instantiating and managing provider-agnostic LLM adapters."""

    @staticmethod
    def get_adapter(provider: Optional[str] = None) -> BaseLLMAdapter:
        selected_provider = (provider or settings.DEFAULT_LLM_PROVIDER or "gemini").lower()

        if selected_provider == "groq" or (not settings.GEMINI_API_KEY and settings.GROQ_API_KEY):
            logger.info(f"Initializing Groq LLM Adapter (Model: {settings.GROQ_MODEL})")
            return GroqAdapter()
        elif selected_provider == "gemini" or settings.GEMINI_API_KEY:
            logger.info(f"Initializing Gemini LLM Adapter (Model: {settings.GEMINI_MODEL})")
            return GeminiAdapter()
        else:
            # If neither key is provided yet, default to Gemini adapter (which will cleanly prompt for key upon call)
            logger.warning("No API key configured for Gemini or Groq. Defaulting to GeminiAdapter.")
            return GeminiAdapter()

# Convenience accessor
def get_llm_service(provider: Optional[str] = None) -> BaseLLMAdapter:
    return LLMFactory.get_adapter(provider=provider)
