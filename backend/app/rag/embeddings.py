import math
import re
import numpy as np
from typing import List
import httpx
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Provides vector embeddings using Gemini API with deterministic dense fallback."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.dim = 384

    async def get_embedding(self, text: str) -> List[float]:
        embeddings = await self.get_embeddings([text])
        return embeddings[0]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.api_key:
            try:
                # Gemini embedding API call
                return await self._call_gemini_embeddings(texts)
            except Exception as e:
                logger.warning(f"Gemini embedding API failed: {e}. Falling back to semantic token hash vectorizer.")
        
        return [self._semantic_hash_embedding(t) for t in texts]

    async def _call_gemini_embeddings(self, texts: List[str]) -> List[List[float]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={self.api_key}"
        requests = [{"model": "models/text-embedding-004", "content": {"parts": [{"text": t[:1000]}]}} for t in texts]
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json={"requests": requests})
            resp.raise_for_status()
            data = resp.json()
            return [emb["values"] for emb in data["embeddings"]]

    def _semantic_hash_embedding(self, text: str) -> List[float]:
        """Deterministic dense representation for testing and offline resilience."""
        vec = np.zeros(self.dim, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec.tolist()

        for i, word in enumerate(words):
            # Map word hash into dimension buckets
            bucket = hash(word) % self.dim
            sign = 1.0 if (hash(word) // self.dim) % 2 == 0 else -1.0
            vec[bucket] += sign * (1.0 / math.sqrt(i + 1))

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
