import unittest
from unittest.mock import patch, MagicMock
from cpa_core.intelligence import CPAAssistant

class TestIntelligence(unittest.TestCase):
    @patch('cpa_core.intelligence.os.path.exists')
    @patch('cpa_core.intelligence.Llama')
    def test_assistant_chat(self, mock_llama, mock_exists):
        # Setup mock exists
        mock_exists.return_value = True
        
        # Setup mock LLM response
        mock_instance = mock_llama.return_value
        mock_instance.return_value = {
            'choices': [{'text': 'This is a test response.'}],
            'usage': {'completion_tokens': 5}
        }
        
        assistant = CPAAssistant(model_path="dummy_path")
        response = assistant.chat("Hello")
        
        self.assertEqual(response, "This is a test response.")
        mock_instance.assert_called_once()

if __name__ == "__main__":
    unittest.main()
