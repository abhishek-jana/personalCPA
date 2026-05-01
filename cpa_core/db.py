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
                content TEXT NOT NULL
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

    def save_document(self, content: str, embedding: list):
        cursor = self.conn.cursor()
        # 1. Insert into document table
        cursor.execute("INSERT INTO documents (content) VALUES (?)", (content,))
        doc_id = cursor.lastrowid
        
        # 2. Insert into VSS table
        # sqlite-vss expects a JSON string or blob for the embedding
        cursor.execute(
            "INSERT INTO vss_documents(rowid, embedding) VALUES (?, ?)",
            (doc_id, json.dumps(embedding))
        )
        self.conn.commit()
        return doc_id

    def search_documents(self, query_embedding: list, limit: int = 5):
        cursor = self.conn.cursor()
        # Join VSS table with documents table to get content
        # vss_search() returns distance, we order by it
        cursor.execute("""
            SELECT 
                d.content,
                v.distance
            FROM vss_documents v
            JOIN documents d ON v.rowid = d.id
            WHERE vss_search(v.embedding, vss_search_params(?, ?))
            ORDER BY v.distance ASC
        """, (json.dumps(query_embedding), limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self.conn.close()
