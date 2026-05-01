import os
from typing import List, Dict, Optional
from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from bs4 import BeautifulSoup
from .db import Database

class KnowledgeBase:
    def __init__(self, db: Database):
        self.db = db
        self._embedder: Optional[TextEmbedding] = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )

    @property
    def embedder(self) -> TextEmbedding:
        if self._embedder is None:
            # Default model: BAAI/bge-small-en-v1.5
            self._embedder = TextEmbedding()
        return self._embedder

    def add_text(self, text: str, collection: str = "default") -> List[int]:
        """Chunks, embeds, and saves text to the vector store."""
        chunks = self._splitter.split_text(text)
        doc_ids = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            embedding = list(self.embedder.embed([chunk]))[0].tolist()
            doc_id = self.db.save_document(chunk, embedding, collection=collection)
            doc_ids.append(doc_id)
        return doc_ids

    def add_file(self, file_path: str, collection: str = None) -> List[int]:
        """Extracts text from a file and adds it to the knowledge base."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # If collection is not provided, use the filename as default collection
        if collection is None:
            collection = os.path.basename(file_path)

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in [".html", ".htm"]:
            text = self._extract_html(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        return self.add_text(text, collection=collection)

    def query(self, text: str, limit: int = 3, collection: str = None) -> List[Dict]:
        """Performs semantic search for relevant context."""
        query_embedding = list(self.embedder.embed([text]))[0].tolist()
        return self.db.search_documents(query_embedding, limit=limit, collection=collection)

    def get_collections(self) -> List[str]:
        """Returns a list of all unique collections."""
        return self.db.get_collections()

    def _extract_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages])

    def _extract_html(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            return soup.get_text()
