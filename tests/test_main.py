from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
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

@patch("main.assistant.chat")
def test_chat_endpoint(mock_chat):
    mock_chat.return_value = "Mocked advice"
    response = client.post("/chat", json={"message": "What is tax?"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Mocked advice"}
    mock_chat.assert_called_once_with("What is tax?")
