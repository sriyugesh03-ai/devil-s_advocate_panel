import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.llm.gemini import GeminiAdapter
from backend.app.llm.groq import GroqAdapter
from backend.app.core.config import settings
from backend.app.core.cache import prompt_cache

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class ResilientLLMAdapter(BaseLLMAdapter):
    """Wrapper that tries primary LLM provider (Gemini/Groq) and automatically falls back to the other on failure."""

    def __init__(self, primary: BaseLLMAdapter, secondary: Optional[BaseLLMAdapter] = None):
        self.primary = primary
        self.secondary = secondary

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        # Check cache first
        cached = prompt_cache.get(
            prompt=prompt,
            system_instruction=system_instruction or "",
            temperature=temperature,
            model=getattr(self.primary, 'model', ''),
        )
        if cached is not None:
            return cached

        try:
            result = await self.primary.generate_text(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.warning(f"Primary LLM adapter failed: {e}.")
            if self.secondary:
                logger.info("Flipping to secondary LLM adapter fallback...")
                result = await self.secondary.generate_text(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                raise e

        # Store in cache
        prompt_cache.put(
            prompt=prompt,
            response=result,
            system_instruction=system_instruction or "",
            temperature=temperature,
            model=getattr(self.primary, 'model', ''),
        )
        return result

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        cache_key_prefix = f"STRUCTURED_{response_model.__name__}::"
        cached_json = prompt_cache.get(
            prompt=cache_key_prefix + prompt,
            system_instruction=system_instruction or "",
            temperature=temperature,
            model=getattr(self.primary, 'model', ''),
        )
        if cached_json is not None:
            try:
                return response_model.model_validate_json(cached_json)
            except Exception:
                pass

        try:
            result = await self.primary.generate_structured(
                prompt=prompt,
                response_model=response_model,
                system_instruction=system_instruction,
                temperature=temperature,
            )
        except Exception as e:
            logger.warning(f"Primary LLM structured generation failed: {e}.")
            if self.secondary:
                logger.info("Flipping to secondary LLM adapter fallback for structured output...")
                result = await self.secondary.generate_structured(
                    prompt=prompt,
                    response_model=response_model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                )
            else:
                raise e

        # Store in cache
        try:
            prompt_cache.put(
                prompt=cache_key_prefix + prompt,
                response=result.model_dump_json(),
                system_instruction=system_instruction or "",
                temperature=temperature,
                model=getattr(self.primary, 'model', ''),
            )
        except Exception:
            pass

        return result

class LLMFactory:
    """Factory creating resilient LLM adapters with auto-fallback between Gemini and Groq."""

    @staticmethod
    def get_adapter(provider: Optional[str] = None) -> BaseLLMAdapter:
        selected_provider = (provider or settings.DEFAULT_LLM_PROVIDER or "gemini").lower()
        
        has_gemini = bool(settings.GEMINI_API_KEY.strip())
        has_groq = bool(settings.GROQ_API_KEY.strip())

        gemini_adapter = GeminiAdapter() if has_gemini else None
        groq_adapter = GroqAdapter() if has_groq else None

        if selected_provider == "groq" and groq_adapter:
            return ResilientLLMAdapter(primary=groq_adapter, secondary=gemini_adapter)
        elif has_gemini and gemini_adapter:
            return ResilientLLMAdapter(primary=gemini_adapter, secondary=groq_adapter)
        elif has_groq and groq_adapter:
            return ResilientLLMAdapter(primary=groq_adapter, secondary=None)
        else:
            # Fallback placeholder
            return GeminiAdapter()

def get_llm_service(provider: Optional[str] = None) -> BaseLLMAdapter:
    return LLMFactory.get_adapter(provider=provider)
