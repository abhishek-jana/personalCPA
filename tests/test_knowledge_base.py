import unittest
from cpa_core.db import Database
from cpa_core.knowledge_base import KnowledgeBase
import os

class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_kb.db"
        self.db = Database(self.db_path)
        self.db.init_db()
        self.kb = KnowledgeBase(self.db)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_text_and_query(self):
        text = "The quick brown fox jumps over the lazy dog."
        doc_ids = self.kb.add_text(text)
        
        self.assertGreater(len(doc_ids), 0)
        
        results = self.kb.query("Who jumps over the dog?", limit=1)
        self.assertEqual(len(results), 1)
        self.assertIn("fox", results[0]["content"])

    def test_add_file_txt(self, tmp_path=None):
        # We'll use a local file for the test
        file_path = "test_kb.txt"
        with open(file_path, "w") as f:
            f.write("Important tax information for 2024.")
        
        try:
            doc_ids = self.kb.add_file(file_path)
            self.assertEqual(len(doc_ids), 1)
            
            results = self.kb.query("What year is the tax info for?")
            self.assertIn("2024", results[0]["content"])
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
