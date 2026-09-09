import pytest
from backend.app.rag.loaders import KnowledgeLoader
from backend.app.rag.chunker import DocumentChunker
from backend.app.rag.embeddings import EmbeddingService
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.retriever import AgentRetriever

@pytest.mark.asyncio
async def test_rag_pipeline():
    loader = KnowledgeLoader("./knowledge")
    docs = loader.load_all_documents()
    assert len(docs) > 0

    chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_documents(docs)
    assert len(chunks) >= len(docs)

    embedding_service = EmbeddingService()
    texts = [c.text for c in chunks[:5]]
    embeddings = await embedding_service.get_embeddings(texts)
    assert len(embeddings) == 5
    assert len(embeddings[0]) == 384

    store = VectorStore(persist_path=None)
    store.add_chunks(chunks[:5], embeddings)
    retriever = AgentRetriever(store, embedding_service)

    res = await retriever.retrieve_for_vc("AI workflow moat", top_k=2)
    assert isinstance(res, list)
