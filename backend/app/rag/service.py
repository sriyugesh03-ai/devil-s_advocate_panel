import logging
import hashlib
from typing import Optional, Dict, Any, List
from backend.app.rag.loaders import KnowledgeLoader
from backend.app.rag.chunker import DocumentChunker
from backend.app.rag.embeddings import EmbeddingService
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.retriever import AgentRetriever
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """End-to-end RAG Service managing ingestion, vector indexing, and persona retrieval."""

    def __init__(self, knowledge_path: str = "./knowledge"):
        self.knowledge_path = knowledge_path
        self.loader = KnowledgeLoader(knowledge_path)
        self.chunker = DocumentChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(persist_path=settings.VECTOR_STORE_PATH)
        self.retriever = AgentRetriever(self.vector_store, self.embedding_service)
        self._is_indexed = False
        # Per-pitch RAG context cache: avoids re-embedding for rounds 2 and 3
        self._context_cache: Dict[str, Dict[str, str]] = {}

    async def initialize_and_index(self):
        # Try loading pre-built index first
        if self.vector_store.load():
            self._is_indexed = True
            logger.info("Loaded pre-indexed knowledge base.")
            return

        logger.info("Building domain knowledge index from raw documents...")
        docs = self.loader.load_all_documents()
        if not docs:
            logger.warning("No knowledge documents found to index.")
            return

        chunks = self.chunker.chunk_documents(docs)
        texts = [c.text for c in chunks]
        embeddings = await self.embedding_service.get_embeddings(texts)
        self.vector_store.add_chunks(chunks, embeddings)
        self.vector_store.persist()
        self._is_indexed = True
        logger.info(f"Successfully indexed {len(chunks)} chunks across domain knowledge bases.")

    def _pitch_cache_key(self, pitch_dict: Dict[str, Any]) -> str:
        """Generate a stable cache key from the pitch contents."""
        raw = f"{pitch_dict.get('title', '')}|{pitch_dict.get('problem', '')}|{pitch_dict.get('solution', '')}|{pitch_dict.get('business_model', '')}|{pitch_dict.get('target_market', '')}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    async def get_contexts_for_pitch(self, pitch_dict: Dict[str, Any]) -> Dict[str, str]:
        """Returns structured grounding context strings for VC, Financial, and Market agents.
        Caches results per-pitch so rounds 2 and 3 return instantly."""
        if not self._is_indexed:
            await self.initialize_and_index()

        cache_key = self._pitch_cache_key(pitch_dict)
        if cache_key in self._context_cache:
            logger.info(f"[RAG CACHE HIT] Returning cached RAG contexts for pitch {cache_key}")
            return self._context_cache[cache_key]

        pitch_text = f"{pitch_dict.get('title', '')} - {pitch_dict.get('problem', '')} - {pitch_dict.get('solution', '')}"
        finance_text = f"{pitch_dict.get('business_model', '')} - {pitch_dict.get('traction', '')}"
        market_text = f"{pitch_dict.get('target_market', '')} - {pitch_dict.get('competition', '')}"

        vc_docs = await self.retriever.retrieve_for_vc(pitch_text)
        fin_docs = await self.retriever.retrieve_for_finance(finance_text)
        mkt_docs = await self.retriever.retrieve_for_market(market_text)

        def format_docs(docs: List[Dict[str, Any]]) -> str:
            if not docs:
                return "No specific benchmark documents retrieved."
            return "\n\n---\n\n".join([f"[{d['domain'].upper()} BENCHMARK / CASE STUDY]:\n{d['text']}" for d in docs])

        contexts = {
            "vc": format_docs(vc_docs),
            "financial": format_docs(fin_docs),
            "market": format_docs(mkt_docs)
        }

        # Cache for subsequent rounds
        self._context_cache[cache_key] = contexts
        logger.info(f"[RAG CACHE MISS] Cached RAG contexts for pitch {cache_key}")
        return contexts

rag_service = RAGService()

