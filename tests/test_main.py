from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
from cpa_core.intelligence import ChatResult
import pytest
import os

client = TestClient(app)

def test_read_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}

def test_create_and_list_transactions():
    transaction_data = {
        "date": "2024-04-30",
        "description": "Coffee",
        "amount": 4.5,
        "category": "Food"
    }
    
    # POST /transactions
    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == 200
    assert response.json()["description"] == "Coffee"
    
    # GET /transactions
    response = client.get("/transactions")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) >= 1
    assert any(t["description"] == "Coffee" for t in transactions)

@patch("main.assistant.ask")
def test_chat_endpoint_with_rag(mock_ask):
    mock_ask.return_value = ChatResult(
        answer="Mocked RAG advice",
        latency=1.0,
        tokens=10,
        tps=10.0
    )
    response = client.post("/chat", json={"message": "What is tax?", "use_rag": True})
    assert response.status_code == 200
    assert response.json()["answer"] == "Mocked RAG advice"

@patch("main.kb.add_text")
def test_add_document_endpoint(mock_add_text):
    mock_add_text.return_value = [1, 2]
    response = client.post("/documents", json={"content": "New document content"})
    assert response.status_code == 200
    assert response.json() == {"ids": [1, 2], "status": "saved"}

def test_dashboard_pulse():
    response = client.get("/dashboard/pulse")
    assert response.status_code == 200
    data = response.json()
    assert "tax_estimate" in data
    assert "savings_rate" in data
    assert "total_spent" in data
    assert isinstance(data["total_spent"], (int, float))

def test_dashboard_inbox():
    # Add an uncategorized transaction to ensure we get an action
    transaction_data = {
        "date": "2024-05-01",
        "description": "Uncategorized Item",
        "amount": 10.0,
        "category": None
    }
    client.post("/transactions", json=transaction_data)
    
    response = client.get("/dashboard/inbox")
    assert response.status_code == 200
    actions = response.json()
    assert isinstance(actions, list)
    if len(actions) > 0:
        assert actions[0]["type"] == "categorization"
        assert "Categorize" in actions[0]["message"]
        assert actions[0]["count"] >= 1
