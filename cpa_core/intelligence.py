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
        
        self.persona = (
            "You are a helpful and accurate CPA Assistant specializing in personal finance and tax advice. "
            "You have access to a Knowledge Base organized into 'Folders' (Collections). "
        )
        self.instructions = (
            "Use the provided context to answer the user's question. "
            "If the user asks about their folders or documents, you should acknowledge that you can see and search them. "
            "If the answer is not in the context, use your general knowledge but mention "
            "it is not in the provided documents."
        )

    def ask(self, message: str, use_rag: bool = True, collection: Optional[str] = None) -> ChatResult:
        # If the user asks specifically about folders, let's inject that info
        if "folder" in message.lower() and self.kb:
            collections = self.kb.get_collections()
            col_list = ", ".join(collections) if collections else "None yet"
            message = f"{message} (System Note: The available folders in the Knowledge Base are: {col_list})"

        if use_rag and self.kb:
            return self._rag_chat(message, collection=collection)
        return self._simple_chat(message)

    def categorize_transactions(self, transactions: List[dict]) -> List[dict]:
        """Automatically assigns categories to a list of transactions."""
        categorized = []
        for t in transactions:
            # Preservation: Don't overwrite existing categories
            if t.get("category"):
                categorized.append(t.copy())
                continue

            description = t.get("description", "Unknown")
            prompt = f"Categorize this transaction description into a single short category name (e.g., Food, Rent, Salary, Travel, Shopping, Utilities, Medical, Insurance, Entertainment, Other):\n\nDescription: {description}\n\nCategory:"
            
            # Minimal implementation for the tracer bullet
            response = self.provider.generate(prompt, stop=["\n"])
            category = response["text"].strip()
            
            # Fallback for empty or confusing responses
            if not category:
                category = "Other"
            
            # Create a copy to avoid mutating original
            new_t = t.copy()
            new_t["category"] = category
            categorized.append(new_t)
            
        return categorized

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

class CPAAuditor:
    def __init__(self, provider: LLMProvider, kb: Any):
        self.provider = provider
        self.kb = kb

    def audit_collection(self, collection_name: str) -> List[Dict]:
        """Verifies if documents in a collection belong there."""
        documents = self.kb.get_documents_in_collection(collection_name)
        anomalies = []

        for doc in documents:
            filename = doc["filename"]
            # Get a sample of the content (first chunk)
            results = self.kb.query(f"What is this document about? {filename}", limit=1, collection=collection_name)
            if not results:
                continue
            
            content_snippet = results[0]["content"][:1000]
            
            prompt = f"""### Instruction:
You are a highly detailed CPA Audit Assistant. Your task is to verify if a document belongs in a specific collection.

### Collection Name: 
{collection_name}

### Document Filename:
{filename}

### Content Snippet:
{content_snippet}

### Question:
Does this document belong in the '{collection_name}' collection? If it seems out of place (e.g., a personal grocery receipt in a 'Tax Knowledge' folder), identify it as an ANOMALY.

Respond with ONLY 'VALID' or 'ANOMALY' followed by a one-sentence reason.

### Answer:
"""
            response = self.provider.generate(prompt, stop=["###"])
            text = response["text"].strip()
            
            if "ANOMALY" in text.upper():
                anomalies.append({
                    "filename": filename,
                    "collection": collection_name,
                    "reason": text.replace("ANOMALY", "").strip(": ").strip()
                })

        return anomalies
