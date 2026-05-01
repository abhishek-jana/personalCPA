import sqlite3
import sqlite_vss
import os

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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT
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

    def close(self):
        self.conn.close()
