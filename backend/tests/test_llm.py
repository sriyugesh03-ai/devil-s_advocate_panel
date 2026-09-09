import pytest
from pydantic import BaseModel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.llm.gemini import GeminiAdapter
from backend.app.llm.groq import GroqAdapter
from backend.app.llm.factory import LLMFactory

class MockResponse(BaseModel):
    summary: str
    score: int

def test_json_parsing_gemini():
    adapter = GeminiAdapter(api_key="mock_key")
    raw_json = '```json\n{"summary": "Solid defensibility", "score": 88}\n```'
    parsed = adapter._parse_json_to_model(raw_json, MockResponse)
    assert parsed.summary == "Solid defensibility"
    assert parsed.score == 88

def test_json_parsing_groq():
    adapter = GroqAdapter(api_key="mock_key")
    raw_json = 'Here is the response:\n{"summary": "High CAC", "score": 45}'
    parsed = adapter._parse_json_to_model(raw_json, MockResponse)
    assert parsed.summary == "High CAC"
    assert parsed.score == 45

def test_factory_selection():
    adapter = LLMFactory.get_adapter("gemini")
    assert isinstance(adapter, BaseLLMAdapter)

