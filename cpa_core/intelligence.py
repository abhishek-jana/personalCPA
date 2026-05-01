import time
import os
import httpx
from typing import Optional, List, Protocol, Dict, Any
from dataclasses import dataclass

@dataclass
class ChatResult:
    answer: str
    latency: float
    tokens: int
    tps: float
    context: Optional[str] = None
    collection_used: Optional[str] = None

class LLMProvider(Protocol):
    def generate(self, prompt: str, stop: List[str]) -> Dict[str, Any]:
        ...

class OllamaProvider:
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def generate(self, prompt: str, stop: List[str]) -> Dict[str, Any]:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "stop": stop,
                        "num_predict": 512
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "text": data["response"],
                "usage": {
                    "completion_tokens": data.get("eval_count", 0)
                }
            }

class LlamaCppProvider:
    def __init__(self, model_path: str, n_gpu_layers: int = 0):
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. "
                "Run 'bash install_llm.sh' or use Ollama instead."
            )
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=os.cpu_count(),
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )

    def generate(self, prompt: str, stop: List[str]) -> Dict[str, Any]:
        response = self.llm(
            prompt,
            max_tokens=512,
            stop=stop,
            echo=False
        )
        return {
            "text": response['choices'][0]['text'],
            "usage": response['usage']
        }

class Searchable(Protocol):
    def query(self, text: str, limit: int = 3, collection: str = None) -> List[dict]:
        ...
    def get_collections(self) -> List[str]:
        ...

class CPAAssistant:
    def __init__(self, provider: LLMProvider, kb: Optional[Searchable] = None):
        self.provider = provider
        self.kb = kb
        
        self.persona = "You are a helpful and accurate CPA Assistant specializing in personal finance and tax advice."
        self.instructions = (
            "Use the provided context to answer the user's question. "
            "If the answer is not in the context, use your general knowledge but mention "
            "it is not in the provided documents."
        )

    def ask(self, message: str, use_rag: bool = True, collection: Optional[str] = None) -> ChatResult:
        if use_rag and self.kb:
            return self._rag_chat(message, collection=collection)
        return self._simple_chat(message)

    def _simple_chat(self, message: str) -> ChatResult:
        prompt = f"### Instruction:\n{self.persona}\n\n### User Question:\n{message}\n\n### Answer:\n"
        return self._inference(prompt, stop=["###", "User Question:"])

    def _rag_chat(self, message: str, collection: Optional[str] = None) -> ChatResult:
        # Smart selection: if collection is not specified, try to infer it
        if not collection:
            collection = self._infer_collection(message)

        results = self.kb.query(message, limit=3, collection=collection)
        context = "\n\n".join([r["content"] for r in results])
        rag_prompt = f"""### Instruction:
{self.persona}
{self.instructions}

### Context:
{context}

### User Question:
{message}

### Answer:
"""
        result = self._inference(rag_prompt, stop=["###", "User Question:"])
        result.context = context
        result.collection_used = collection
        return result

    def _infer_collection(self, message: str) -> Optional[str]:
        """Heuristic-based collection selection."""
        if not self.kb:
            return None
            
        collections = self.kb.get_collections()
        if not collections:
            return None

        msg_lower = message.lower()
        
        # Keyword-based mapping
        mapping = {
            "tax": ["tax knowledge", "tax basics", "1040", "irs"],
            "spent": ["bank statements", "credit card", "grocery", "spending"],
            "income": ["salary", "w2", "1099"],
            "prior": ["prior returns", "2022", "2021"]
        }

        for key, aliases in mapping.items():
            if key in msg_lower or any(a in msg_lower for a in aliases):
                # Find if any of our actual collections match these aliases
                for c in collections:
                    if any(a in c.lower() for a in [key] + aliases):
                        return c
        
        return None

    def _inference(self, prompt: str, stop: List[str]) -> ChatResult:
        start_time = time.time()
        response = self.provider.generate(prompt, stop=stop)
        end_time = time.time()
        
        latency = end_time - start_time
        answer = response['text'].strip()
        tokens = response['usage']['completion_tokens']
        tps = tokens / latency if latency > 0 else 0
        
        return ChatResult(
            answer=answer,
            latency=latency,
            tokens=tokens,
            tps=tps
        )
