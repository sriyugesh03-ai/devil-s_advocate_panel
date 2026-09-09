import json
import logging
import re
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini Adapter supporting gemini-2.5-flash / gemini-1.5-pro with structured output."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
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

        endpoint = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Gemini response: {data}")
                raise ValueError(f"Unexpected response structure from Gemini API: {e}")

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

        # Regex fallback to find first JSON object or array
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

        try:
            parsed = json.loads(cleaned)
            return model_cls.model_validate(parsed)
        except Exception as e:
            logger.error(f"JSON validation error for {model_cls.__name__}: {e}. Raw content: {cleaned[:500]}")
            raise ValueError(f"Could not parse LLM output into {model_cls.__name__}: {e}")
