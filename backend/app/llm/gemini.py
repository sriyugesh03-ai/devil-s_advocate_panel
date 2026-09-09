import json
import logging
import re
import asyncio
from typing import Optional, Type, TypeVar, List
import httpx
from pydantic import BaseModel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini Adapter with automatic model fallback, retry on 429 rate limits, and structured JSON parsing."""

    # Ordered list of valid Gemini models to fallback across
    CANDIDATE_MODELS = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (api_key or settings.GEMINI_API_KEY).strip()
        requested_model = (model or settings.GEMINI_MODEL or "gemini-2.5-flash").strip()
        # If model name has non-existent version like 3.5, start with 2.5-flash
        if requested_model == "gemini-3.5-flash":
            self.model = "gemini-2.5-flash"
        else:
            self.model = requested_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment.")

        models_to_try = [self.model] + [m for m in self.CANDIDATE_MODELS if m != self.model]
        last_error = None

        for model_name in models_to_try:
            endpoint = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            # Try up to 2 retries per model for rate limits
            for attempt in range(2):
                try:
                    async with httpx.AsyncClient(timeout=35.0) as client:
                        response = await client.post(endpoint, json=payload)
                        
                        if response.status_code == 429:
                            logger.warning(f"Gemini {model_name} rate limit (429) on attempt {attempt+1}. Backing off...")
                            await asyncio.sleep(1.5 * (attempt + 1))
                            continue

                        response.raise_for_status()
                        data = response.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        self.model = model_name  # Stick with the working model
                        return text.strip()

                except Exception as e:
                    last_error = e
                    logger.warning(f"Gemini call with {model_name} (attempt {attempt+1}) encountered: {e}")
                    if attempt == 0 and "429" in str(e):
                        await asyncio.sleep(1.5)

        raise last_error or ValueError("All Gemini candidate models failed.")

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        enriched_prompt = (
            f"{prompt}\n\n"
            f"IMPORTANT: You MUST respond ONLY with valid JSON matching the following JSON Schema. "
            f"Do not include markdown code block backticks, just raw JSON:\n\n"
            f"{schema_json}"
        )

        raw_output = await self.generate_text(
            prompt=enriched_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=4096,
        )

        return self._parse_json_to_model(raw_output, response_model)

    def _parse_json_to_model(self, text: str, model_cls: Type[T]) -> T:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

        try:
            parsed = json.loads(cleaned)
            return model_cls.model_validate(parsed)
        except Exception as e:
            logger.error(f"JSON validation error for {model_cls.__name__}: {e}. Raw: {cleaned[:300]}")
            raise ValueError(f"Could not parse LLM output into {model_cls.__name__}: {e}")
