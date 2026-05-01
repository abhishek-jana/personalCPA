import unittest
from unittest.mock import patch, MagicMock
from cpa_core.intelligence import CPAAssistant

class TestIntelligence(unittest.TestCase):
    @patch('cpa_core.intelligence.os.path.exists')
    @patch('cpa_core.intelligence.Llama')
    def test_assistant_ask_simple(self, mock_llama, mock_exists):
        # Setup mock exists
        mock_exists.return_value = True
        
        # Setup mock LLM response
        mock_instance = mock_llama.return_value
        mock_instance.return_value = {
            'choices': [{'text': 'Simple response.'}],
            'usage': {'completion_tokens': 5}
        }
        
        assistant = CPAAssistant(model_path="dummy_path")
        response = assistant.ask("Hello", use_rag=False)
        
        self.assertEqual(response, "Simple response.")
        mock_instance.assert_called_once()

    @patch('cpa_core.intelligence.os.path.exists')
    @patch('cpa_core.intelligence.Llama')
    def test_assistant_ask_rag(self, mock_llama, mock_exists):
        mock_exists.return_value = True
        mock_instance = mock_llama.return_value
        mock_instance.return_value = {
            'choices': [{'text': 'Context-based answer.'}],
            'usage': {'completion_tokens': 5}
        }
        
        # Mock KnowledgeBase
        mock_kb = MagicMock()
        mock_kb.query.return_value = [{"content": "Important context", "distance": 0.1}]
        
        assistant = CPAAssistant(model_path="dummy_path", kb=mock_kb)
        response = assistant.ask("Query", use_rag=True)
        
        self.assertEqual(response, "Context-based answer.")
        mock_kb.query.assert_called_once_with("Query", limit=3)

if __name__ == "__main__":
    unittest.main()
