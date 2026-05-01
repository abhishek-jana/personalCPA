import sqlite3
import sqlite_vss
import os
import json

class Database:
    def __init__(self, db_path="cpa.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._load_extensions()

    def _load_extensions(self):
        self.conn.enable_load_extension(True)
        sqlite_vss.load(self.conn)

    def init_db(self):
        cursor = self.conn.cursor()
        # Standard transaction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT
            )
        """)
        
        # Document table for RAG content
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                collection TEXT
            )
        """)
        
        # Virtual table for vector search
        # 384 dimensions for BGE-small-en-v1.5
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vss_documents USING vss0(
                embedding(384)
            )
        """)
        
        self.conn.commit()

    def save_transaction(self, transaction: dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, category)
            VALUES (?, ?, ?, ?)
        """, (
            transaction["date"],
            transaction["description"],
            transaction["amount"],
            transaction.get("category")
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def save_document(self, content: str, embedding: list, collection: str = "default"):
        """Internal method used by KnowledgeBase."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO documents (content, collection) VALUES (?, ?)", 
            (content, collection)
        )
        doc_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO vss_documents(rowid, embedding) VALUES (?, ?)",
            (doc_id, json.dumps(embedding))
        )
        self.conn.commit()
        return doc_id

    def search_documents(self, query_embedding: list, limit: int = 5, collection: str = None):
        """Internal method used by KnowledgeBase."""
        cursor = self.conn.cursor()
        
        # Prevent crash if no documents are indexed
        cursor.execute("SELECT count(*) FROM vss_documents")
        if cursor.fetchone()[0] == 0:
            return []

        # Faiss requires k > 0
        limit = max(1, limit)

        query = """
            SELECT 
                d.content,
                v.distance,
                d.collection
            FROM vss_documents v
            JOIN documents d ON v.rowid = d.id
            WHERE vss_search(v.embedding, vss_search_params(?, ?))
        """
        params = [json.dumps(query_embedding), limit]

        if collection:
            query += " AND d.collection = ?"
            params.append(collection)

        query += " ORDER BY v.distance ASC"

        cursor.execute(query, tuple(params))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_collections(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT collection FROM documents WHERE collection IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()
