import unittest
from unittest.mock import MagicMock
from cpa_core.intelligence import CPAAssistant, ChatResult

class TestCategorization(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MagicMock()
        self.assistant = CPAAssistant(provider=self.mock_provider)

    def test_categorize_single_transaction(self):
        """RED: Test that a single transaction is categorized correctly."""
        # Setup mock LLM response
        self.mock_provider.generate.return_value = {
            'text': 'Food & Dining',
            'usage': {'completion_tokens': 5}
        }

        transactions = [
            {"description": "Grocery Store", "amount": -50.25}
        ]
        
        categorized = self.assistant.categorize_transactions(transactions)
        
        self.assertEqual(len(categorized), 1)
        self.assertEqual(categorized[0]["category"], "Food & Dining")
        self.assertEqual(categorized[0]["description"], "Grocery Store")

    def test_preserves_existing_category(self):
        """RED: Test that existing categories are not overwritten."""
        transactions = [
            {"description": "Grocery Store", "amount": -50.25, "category": "Custom Category"}
        ]
        
        categorized = self.assistant.categorize_transactions(transactions)
        
        self.assertEqual(categorized[0]["category"], "Custom Category")
        # Ensure generate was NEVER called
        self.mock_provider.generate.assert_not_called()

    def test_batch_categorization(self):
        """GREEN: Test that multiple transactions are categorized in one pass."""
        self.mock_provider.generate.side_effect = [
            {'text': 'Salary', 'usage': {'completion_tokens': 2}},
            {'text': 'Rent', 'usage': {'completion_tokens': 2}}
        ]

        transactions = [
            {"description": "Company Payroll", "amount": 3000.00},
            {"description": "Apartment Rent", "amount": -1200.00}
        ]
        
        categorized = self.assistant.categorize_transactions(transactions)
        
        self.assertEqual(len(categorized), 2)
        self.assertEqual(categorized[0]["category"], "Salary")
        self.assertEqual(categorized[1]["category"], "Rent")

    def test_fallback_for_unknown_response(self):
        """RED: Test that unknown or empty responses fallback to 'Other'."""
        self.mock_provider.generate.return_value = {
            'text': '', # Empty response
            'usage': {'completion_tokens': 0}
        }
        
        transactions = [
            {"description": "??? cryptic ???", "amount": -1.00}
        ]
        
        categorized = self.assistant.categorize_transactions(transactions)
        
        self.assertEqual(categorized[0]["category"], "Other")

if __name__ == "__main__":
    unittest.main()
