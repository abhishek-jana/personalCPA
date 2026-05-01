import pytest
import os
from cpa_core.db import Database

@pytest.fixture
def db():
    # Use a temporary file for the database during tests
    db_path = "test_cpa.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    database = Database(db_path)
    database.init_db()
    yield database
    
    if os.path.exists(db_path):
        os.remove(db_path)

def test_save_and_get_transaction(db):
    transaction = {
        "date": "2024-04-30",
        "description": "Grocery",
        "amount": 50.0,
        "category": "Food"
    }
    db.save_transaction(transaction)
    
    transactions = db.get_transactions()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Grocery"
    assert transactions[0]["amount"] == 50.0
    assert transactions[0]["date"] == "2024-04-30"
    assert transactions[0]["category"] == "Food"
    assert "id" in transactions[0]

def test_vss_extension_loaded(db):
    # Verify sqlite-vss is loaded by checking for a vss function or table
    # vss_version() is a function provided by sqlite-vss
    cursor = db.conn.cursor()
    cursor.execute("select vss_version();")
    version = cursor.fetchone()[0]
    assert version is not None
    print(f"vss version: {version}")
