from llama_cpp import Llama
import os
from typing import Optional

class CPAAssistant:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._llm: Optional[Llama] = None

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

    def chat(self, message: str) -> str:
        prompt = f"Q: {message}\nA:"
        response = self.llm(
            prompt,
            max_tokens=512,
            stop=["Q:", "\n"],
            echo=False
        )
        return response['choices'][0]['text'].strip()

    def rag_chat(self, message: str, kb: any) -> str:
        """Perform RAG by retrieving context from the KnowledgeBase before chatting."""
        # 1. Search KB
        results = kb.query(message, limit=3)
        context = "\n\n".join([r["content"] for r in results])
        
        # 2. Construct prompt
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
