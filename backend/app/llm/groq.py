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

class GroqAdapter(BaseLLMAdapter):
    """Groq API Adapter supporting high-speed inference with model fallbacks and retries."""

    CANDIDATE_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (api_key or settings.GROQ_API_KEY).strip()
        requested_model = (model or settings.GROQ_MODEL or "llama-3.3-70b-versatile").strip()
        if requested_model == "openai/gpt-oss 120b":
            self.model = "llama-3.3-70b-versatile"
        else:
            self.model = requested_model
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

        models_to_try = [self.model] + [m for m in self.CANDIDATE_MODELS if m != self.model]
        last_error = None

        for model_name in models_to_try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            for attempt in range(2):
                try:
                    async with httpx.AsyncClient(timeout=35.0) as client:
                        response = await client.post(self.base_url, headers=headers, json=payload)
                        if response.status_code == 429:
                            logger.warning(f"Groq {model_name} rate limit (429) on attempt {attempt+1}. Backing off...")
                            await asyncio.sleep(1.0 * (attempt + 1))
                            continue

                        response.raise_for_status()
                        data = response.json()
                        self.model = model_name
                        return data["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    last_error = e
                    logger.warning(f"Groq call with {model_name} encountered: {e}")
                    if attempt == 0 and "429" in str(e):
                        await asyncio.sleep(1.0)

        raise last_error or ValueError("All Groq candidate models failed.")

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
            logger.error(f"JSON validation error for {model_cls.__name__}: {e}. Raw content: {cleaned[:300]}")
            raise ValueError(f"Could not parse Groq output into {model_cls.__name__}: {e}")
