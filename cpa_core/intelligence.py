from llama_cpp import Llama
from fastembed import TextEmbedding
import os
from typing import Optional, List

class CPAAssistant:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._llm: Optional[Llama] = None
        self._embedder: Optional[TextEmbedding] = None

    @property
    def llm(self) -> Llama:
        if self._llm is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")
            
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=os.cpu_count(),
                verbose=False
            )
        return self._llm

    @property
    def embedder(self) -> TextEmbedding:
        if self._embedder is None:
            # Default model is BAAI/bge-small-en-v1.5, very lightweight
            self._embedder = TextEmbedding()
        return self._embedder

    def chat(self, message: str) -> str:
        prompt = f"Q: {message}\nA:"
        response = self.llm(
            prompt,
            max_tokens=512,
            stop=["Q:", "\n"],
            echo=False
        )
        return response['choices'][0]['text'].strip()

    def rag_chat(self, message: str, db: any) -> str:
        """Perform RAG by retrieving context from the database before chatting."""
        # 1. Embed query
        query_embedding = self.embed(message)
        
        # 2. Search DB
        results = db.search_documents(query_embedding, limit=3)
        context = "\n\n".join([r["content"] for r in results])
        
        # 3. Construct prompt
        rag_prompt = f"""### Instructions:
You are a helpful and accurate CPA Assistant. Use the following pieces of context to answer the user's question.
If the answer is not in the context, use your general knowledge but mention it is not in the provided documents.

### Context:
{context}

### User Question:
{message}

### Answer:
"""
        
        response = self.llm(
            rag_prompt,
            max_tokens=512,
            stop=["###", "User Question:"],
            echo=False
        )
        return response['choices'][0]['text'].strip()

    def embed(self, text: str) -> List[float]:
        """Generate vector embedding for a given text."""
        # list() is needed as embed() returns a generator
        embeddings = list(self.embedder.embed([text]))
        return embeddings[0].tolist()
