"""
In-memory LRU prompt cache for LLM responses.
Eliminates redundant LLM calls for identical prompts, dramatically reducing
latency for repeated questions (e.g. same pitch across rounds).
"""

import hashlib
import time
import logging
from typing import Optional, Dict, Any
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)


class PromptCache:
    """Thread-safe in-memory LRU cache for LLM prompt/response pairs."""

    def __init__(self, max_size: int = 256, ttl_seconds: int = 1800):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds  # Default 30 min
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_key(
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        model: str = "",
    ) -> str:
        raw = f"{system_instruction}||{prompt}||{temperature}||{model}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        model: str = "",
    ) -> Optional[str]:
        key = self._hash_key(prompt, system_instruction, temperature, model)
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                # Check TTL
                if time.time() - entry["timestamp"] < self.ttl_seconds:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    logger.info(f"[CACHE HIT] Prompt cache hit (hits={self._hits})")
                    return entry["response"]
                else:
                    # Expired
                    del self._cache[key]
            self._misses += 1
            return None

    def put(
        self,
        prompt: str,
        response: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        model: str = "",
    ) -> None:
        key = self._hash_key(prompt, system_instruction, temperature, model)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = {"response": response, "timestamp": time.time()}
            else:
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)  # Evict oldest
                self._cache[key] = {"response": response, "timestamp": time.time()}

    @property
    def stats(self) -> Dict[str, int]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "hit_rate": round(self._hits / max(self._hits + self._misses, 1) * 100, 1),
        }


# Global singleton
prompt_cache = PromptCache()
