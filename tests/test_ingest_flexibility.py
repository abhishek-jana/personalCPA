import unittest
import os
import csv
from cpa_core.ingest import parse_csv

class TestIngestFlexibility(unittest.TestCase):
    def setUp(self):
        self.test_file = "flexible_test.csv"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("date,DESCRIPTION,amt\n")
            f.write("2023-10-01,Test 1,100.00\n")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_case_insensitive_headers_fail(self):
        # This should fail because 'amt' is not 'amount'
        with self.assertRaises(ValueError):
            parse_csv(self.test_file)

    def test_case_insensitive_headers_pass(self):
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("DATE,description,Amount\n")
            f.write("2023-10-01,Test 1,100.00\n")
        
        transactions = parse_csv(self.test_file)
        self.assertEqual(transactions[0]["description"], "Test 1")
        self.assertEqual(transactions[0]["amount"], 100.0)

if __name__ == "__main__":
    unittest.main()
