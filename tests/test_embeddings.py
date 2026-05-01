import unittest
from cpa_core.intelligence import CPAAssistant

class TestEmbeddings(unittest.TestCase):
    def test_embed_text(self):
        # We don't need a model path for embeddings if we use fastembed's default
        assistant = CPAAssistant(model_path="models/Phi-3-mini-4k-instruct-q4.gguf")
        text = "This is a test document about taxes."
        embedding = assistant.embed(text)
        
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)
        self.assertIsInstance(embedding[0], float)

if __name__ == "__main__":
    unittest.main()
