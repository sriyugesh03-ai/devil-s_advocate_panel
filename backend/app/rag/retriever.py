from typing import List, Dict, Any, Optional
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.embeddings import EmbeddingService

class AgentRetriever:
    """Specialized retriever providing persona-tuned domain knowledge retrieval."""

    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def retrieve_for_vc(self, pitch_summary: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = await self.embedding_service.get_embedding(f"moats defensibility scale competition: {pitch_summary}")
        # Search business and competition domains
        res_biz = self.vector_store.similarity_search(query_vec, top_k=top_k, domain_filter="business")
        res_comp = self.vector_store.similarity_search(query_vec, top_k=1, domain_filter="competition")
        return res_biz + res_comp

    async def retrieve_for_finance(self, financial_summary: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = await self.embedding_service.get_embedding(f"unit economics CAC LTV gross margin burn: {financial_summary}")
        return self.vector_store.similarity_search(query_vec, top_k=top_k, domain_filter="finance")

    async def retrieve_for_market(self, market_summary: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = await self.embedding_service.get_embedding(f"market size TAM timing incumbent retaliation: {market_summary}")
        res_mkt = self.vector_store.similarity_search(query_vec, top_k=top_k, domain_filter="market")
        res_comp = self.vector_store.similarity_search(query_vec, top_k=1, domain_filter="competition")
        return res_mkt + res_comp
