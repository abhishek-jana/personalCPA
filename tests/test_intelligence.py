import unittest
from unittest.mock import MagicMock, patch
from cpa_core.intelligence import CPAAssistant, ChatResult, OllamaProvider

class TestIntelligence(unittest.TestCase):
    def test_assistant_ask_simple_with_mock_provider(self):
        # Setup mock provider
        mock_provider = MagicMock()
        mock_provider.generate.return_value = {
            'text': 'Simple response.',
            'usage': {'completion_tokens': 5}
        }
        
        assistant = CPAAssistant(provider=mock_provider)
        result = assistant.ask("Hello", use_rag=False)
        
        self.assertIsInstance(result, ChatResult)
        self.assertEqual(result.answer, "Simple response.")
        mock_provider.generate.assert_called_once()

    def test_assistant_ask_rag_with_mock_provider(self):
        # Setup mock provider
        mock_provider = MagicMock()
        mock_provider.generate.return_value = {
            'text': 'Context-based answer.',
            'usage': {'completion_tokens': 5}
        }
        
        # Mock KnowledgeBase
        mock_kb = MagicMock()
        mock_kb.query.return_value = [{"content": "Important context", "distance": 0.1}]
        mock_kb.get_collections.return_value = []
        
        assistant = CPAAssistant(provider=mock_provider, kb=mock_kb)
        result = assistant.ask("Query", use_rag=True)
        
        self.assertIsInstance(result, ChatResult)
        self.assertEqual(result.answer, "Context-based answer.")
        self.assertEqual(result.context, "Important context")
        # In the new implementation, it calls query with collection=None by default
        mock_kb.query.assert_called_once_with("Query", limit=3, collection=None)

    def test_smart_collection_inference(self):
        mock_provider = MagicMock()
        mock_provider.generate.return_value = {
            'text': 'Inferred answer.',
            'usage': {'completion_tokens': 5}
        }

        mock_kb = MagicMock()
        mock_kb.get_collections.return_value = ["Bank Statements", "IRS Instructions"]
        mock_kb.query.return_value = []

        assistant = CPAAssistant(provider=mock_provider, kb=mock_kb)
        
        # Test tax inference
        assistant.ask("What is my tax bracket?")
        mock_kb.query.assert_called_with("What is my tax bracket?", limit=3, collection="IRS Instructions")

        # Test spending inference
        assistant.ask("How much did I spent on groceries?")
        mock_kb.query.assert_called_with("How much did I spent on groceries?", limit=3, collection="Bank Statements")

    @patch('httpx.Client')
    def test_ollama_provider(self, mock_client_class):
        # Mock httpx client and response
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Ollama answer",
            "eval_count": 10
        }
        mock_client.post.return_value = mock_response
        
        provider = OllamaProvider(model_name="phi3")
        result = provider.generate("Test prompt", stop=["###"])
        
        self.assertEqual(result["text"], "Ollama answer")
        self.assertEqual(result["usage"]["completion_tokens"], 10)

if __name__ == "__main__":
    unittest.main()
