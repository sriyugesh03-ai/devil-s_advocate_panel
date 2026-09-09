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

class GroqAdapter(BaseLLMAdapter):
    """Groq API Adapter supporting high-speed inference (e.g., openai/gpt-oss 120b, llama-3.3-70b-versatile)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL or "openai/gpt-oss 120b"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured in environment.")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Groq response: {data}")
                raise ValueError(f"Unexpected response structure from Groq API: {e}")

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_with_schema = (
            (system_instruction or "You are an expert AI system.")
            + "\n\nCRITICAL: Respond ONLY with a valid JSON object matching this schema. "
            + "Do not wrap in markdown or backticks:\n"
            + schema_json
        )

        raw_output = await self.generate_text(
            prompt=prompt,
            system_instruction=system_with_schema,
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
            logger.error(f"JSON validation error for {model_cls.__name__}: {e}. Raw content: {cleaned[:500]}")
            raise ValueError(f"Could not parse Groq output into {model_cls.__name__}: {e}")
