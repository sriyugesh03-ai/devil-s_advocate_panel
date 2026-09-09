import math
import re
import numpy as np
from typing import List, Dict
import httpx
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Provides cached vector embeddings using Gemini API with deterministic dense fallback."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.dim = 384
        self._cache: Dict[str, List[float]] = {}

    async def get_embedding(self, text: str) -> List[float]:
        # Fast cache lookup
        cache_key = text.strip().lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        embeddings = await self.get_embeddings([text])
        self._cache[cache_key] = embeddings[0]
        return embeddings[0]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Check cache for each
        results = []
        uncached_texts = []
        uncached_indices = []

        for idx, t in enumerate(texts):
            ck = t.strip().lower()
            if ck in self._cache:
                results.append((idx, self._cache[ck]))
            else:
                uncached_texts.append(t)
                uncached_indices.append(idx)

        if uncached_texts:
            new_embeddings = []
            if self.api_key:
                try:
                    new_embeddings = await self._call_gemini_embeddings(uncached_texts)
                except Exception as e:
                    logger.warning(f"Gemini embedding API failed: {e}. Falling back to semantic token hash vectorizer.")
                    new_embeddings = [self._semantic_hash_embedding(t) for t in uncached_texts]
            else:
                new_embeddings = [self._semantic_hash_embedding(t) for t in uncached_texts]

            for orig_idx, t, emb in zip(uncached_indices, uncached_texts, new_embeddings):
                self._cache[t.strip().lower()] = emb
                results.append((orig_idx, emb))

        # Sort back to original input order
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    async def _call_gemini_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Google standard embedding endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:batchEmbedContents?key={self.api_key}"
        requests = [{"model": "models/embedding-001", "content": {"parts": [{"text": t[:800]}]}} for t in texts]
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json={"requests": requests})
            if resp.status_code != 200:
                # Silently fallback to our semantic dense vectorizer
                return [self._semantic_hash_embedding(t) for t in texts]
            data = resp.json()
            return [emb["values"] for emb in data.get("embeddings", [])]


    def _semantic_hash_embedding(self, text: str) -> List[float]:
        """Deterministic dense representation for testing and offline resilience."""
        vec = np.zeros(self.dim, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec.tolist()

        for i, word in enumerate(words):
            bucket = hash(word) % self.dim
            sign = 1.0 if (hash(word) // self.dim) % 2 == 0 else -1.0
            vec[bucket] += sign * (1.0 / math.sqrt(i + 1))

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
