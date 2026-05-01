import unittest
import os
from cpa_core.ingest import parse_csv

class TestIngest(unittest.TestCase):
    def test_parse_csv(self):
        file_path = "test_data/sample.csv"
        # Ensure we are in the right directory or provide absolute path
        abs_path = os.path.abspath(file_path)
        transactions = parse_csv(abs_path)
        
        expected = [
            {"date": "2023-10-01", "description": "Grocery Store", "amount": -50.25},
            {"date": "2023-10-02", "description": "Salary", "amount": 3000.00},
            {"date": "2023-10-03", "description": "Rent", "amount": -1200.0}
        ]
        
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions, expected)

if __name__ == "__main__":
    unittest.main()
