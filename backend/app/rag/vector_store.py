import numpy as np
from typing import List, Dict, Any, Optional
import os
import json
import logging
from backend.app.rag.chunker import DocumentChunk

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector database with metadata filtering and persistent JSON index storage."""

    def __init__(self, persist_path: Optional[str] = "./data/vectorstore"):
        self.persist_path = persist_path
        self.chunks: List[DocumentChunk] = []
        self.vectors: List[np.ndarray] = []

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        for chunk, emb in zip(chunks, embeddings):
            self.chunks.append(chunk)
            self.vectors.append(np.array(emb, dtype=np.float32))
        logger.info(f"Vector store indexed {len(chunks)} chunks. Total: {len(self.chunks)}")

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.vectors:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        results = []
        for idx, (chunk, v) in enumerate(zip(self.chunks, self.vectors)):
            if domain_filter and chunk.domain != domain_filter:
                continue

            v_norm = np.linalg.norm(v)
            if v_norm == 0:
                similarity = 0.0
            else:
                # Cosine similarity
                similarity = float(np.dot(q_vec, v) / (q_norm * v_norm))

            results.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "domain": chunk.domain,
                "source": chunk.source,
                "score": round(similarity, 4),
                "metadata": chunk.metadata
            })

        # Sort by similarity descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def persist(self):
        if not self.persist_path:
            return
        os.makedirs(self.persist_path, exist_ok=True)
        index_file = os.path.join(self.persist_path, "index.json")
        data = {
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "text": c.text,
                    "domain": c.domain,
                    "source": c.source,
                    "metadata": c.metadata,
                }
                for c in self.chunks
            ],
            "vectors": [v.tolist() for v in self.vectors]
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        logger.info(f"Persisted vector store index to {index_file}")

    def load(self) -> bool:
        if not self.persist_path:
            return False
        index_file = os.path.join(self.persist_path, "index.json")
        if not os.path.exists(index_file):
            return False

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.chunks = [
                DocumentChunk(
                    text=c["text"],
                    domain=c["domain"],
                    source=c["source"],
                    chunk_id=c["chunk_id"],
                    metadata=c.get("metadata", {})
                )
                for c in data["chunks"]
            ]
            self.vectors = [np.array(v, dtype=np.float32) for v in data["vectors"]]
            logger.info(f"Loaded {len(self.chunks)} chunks from persistent vector index.")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            return False
