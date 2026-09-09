import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class KnowledgeDocument:
    def __init__(self, content: str, domain: str, filename: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.domain = domain
        self.filename = filename
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<KnowledgeDocument domain={self.domain} file={self.filename} chars={len(self.content)}>"

class KnowledgeLoader:
    """Loads knowledge corpus from directory structures."""

    def __init__(self, knowledge_base_path: str = "./knowledge"):
        # Auto-resolve relative to project root if './knowledge' is not in cwd
        if not os.path.exists(knowledge_base_path) and os.path.exists(os.path.join("..", "knowledge")):
            self.knowledge_base_path = os.path.join("..", "knowledge")
        else:
            self.knowledge_base_path = knowledge_base_path


    def load_all_documents(self) -> List[KnowledgeDocument]:
        documents: List[KnowledgeDocument] = []
        if not os.path.exists(self.knowledge_base_path):
            logger.warning(f"Knowledge directory '{self.knowledge_base_path}' does not exist.")
            return documents

        for domain in os.listdir(self.knowledge_base_path):
            domain_path = os.path.join(self.knowledge_base_path, domain)
            if os.path.isdir(domain_path):
                for filename in os.listdir(domain_path):
                    if filename.endswith((".md", ".txt")):
                        file_path = os.path.join(domain_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                text = f.read()
                            documents.append(
                                KnowledgeDocument(
                                    content=text,
                                    domain=domain,
                                    filename=filename,
                                    metadata={"source": file_path, "domain": domain, "filename": filename}
                                )
                            )
                        except Exception as e:
                            logger.error(f"Error loading document {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} knowledge documents from {self.knowledge_base_path}")
        return documents
