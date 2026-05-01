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
