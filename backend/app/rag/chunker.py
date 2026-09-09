from typing import List, Dict, Any
from backend.app.rag.loaders import KnowledgeDocument

class DocumentChunk:
    def __init__(self, text: str, domain: str, source: str, chunk_id: str, metadata: Dict[str, Any] = None):
        self.text = text
        self.domain = domain
        self.source = source
        self.chunk_id = chunk_id
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<DocumentChunk id={self.chunk_id} domain={self.domain} chars={len(self.text)}>"

class DocumentChunker:
    """Chunks documents into retrievable passages while preserving domain metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents: List[KnowledgeDocument]) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []

        for doc in documents:
            paragraphs = [p.strip() for p in doc.content.split("\n\n") if p.strip()]
            current_chunk = ""
            chunk_idx = 0

            for p in paragraphs:
                if len(current_chunk) + len(p) + 2 <= self.chunk_size:
                    current_chunk = f"{current_chunk}\n\n{p}".strip() if current_chunk else p
                else:
                    if current_chunk:
                        chunk_id = f"{doc.domain}_{doc.filename}_{chunk_idx}"
                        chunks.append(
                            DocumentChunk(
                                text=current_chunk,
                                domain=doc.domain,
                                source=doc.filename,
                                chunk_id=chunk_id,
                                metadata={**doc.metadata, "chunk_id": chunk_id}
                            )
                        )
                        chunk_idx += 1
                    current_chunk = p

            if current_chunk:
                chunk_id = f"{doc.domain}_{doc.filename}_{chunk_idx}"
                chunks.append(
                    DocumentChunk(
                        text=current_chunk,
                        domain=doc.domain,
                        source=doc.filename,
                        chunk_id=chunk_id,
                        metadata={**doc.metadata, "chunk_id": chunk_id}
                    )
                )

        return chunks
