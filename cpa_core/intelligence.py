from llama_cpp import Llama
import os
from typing import Optional, List, Protocol

class Searchable(Protocol):
    def query(self, text: str, limit: int = 3) -> List[dict]:
        ...

class CPAAssistant:
    def __init__(self, model_path: str, kb: Optional[Searchable] = None):
        self.model_path = model_path
        self.kb = kb
        self._llm: Optional[Llama] = None
        
        # Internalized Persona & Prompts
        self.persona = "You are a helpful and accurate CPA Assistant specializing in personal finance and tax advice."
        self.instructions = (
            "Use the provided context to answer the user's question. "
            "If the answer is not in the context, use your general knowledge but mention "
            "it is not in the provided documents."
        )

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

    def ask(self, message: str, use_rag: bool = True) -> str:
        """The primary high-leverage interface for the assistant."""
        if use_rag and self.kb:
            return self._rag_chat(message)
        return self._simple_chat(message)

    def _simple_chat(self, message: str) -> str:
        prompt = f"### Instruction:\n{self.persona}\n\n### User Question:\n{message}\n\n### Answer:\n"
        return self._inference(prompt, stop=["###", "User Question:"])

    def _rag_chat(self, message: str) -> str:
        # 1. Retrieve context from memory
        results = self.kb.query(message, limit=3)
        context = "\n\n".join([r["content"] for r in results])
        
        # 2. Construct grounded prompt
        rag_prompt = f"""### Instruction:
{self.persona}
{self.instructions}

### Context:
{context}

### User Question:
{message}

### Answer:
"""
        return self._inference(rag_prompt, stop=["###", "User Question:"])

    def _inference(self, prompt: str, stop: List[str]) -> str:
        response = self.llm(
            prompt,
            max_tokens=512,
            stop=stop,
            echo=False
        )
        return response['choices'][0]['text'].strip()
