import unittest
from cpa_core.db import Database
import os

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_vector.db"
        self.db = Database(self.db_path)
        self.db.init_db()

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_vector_search(self):
        # Sample data
        text = "Taxes are due on April 15th."
        # BGE-small embedding is 384 dimensions
        embedding = [0.1] * 384
        
        # Save to DB
        self.db.save_document(text, embedding)
        
        # Search
        results = self.db.search_documents(embedding, limit=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], text)

if __name__ == "__main__":
    unittest.main()
