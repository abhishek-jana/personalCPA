from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from cpa_core.db import Database
from cpa_core.ingest import parse_csv
import os
import shutil

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database("cpa.db")
db.init_db()

class Transaction(BaseModel):
    id: Optional[int] = None
    date: str
    description: str
    amount: float
    category: Optional[str] = None

@app.get("/status")
def read_status():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction):
    transaction_id = db.save_transaction(transaction.model_dump())
    transaction.id = transaction_id
    return transaction

@app.get("/transactions", response_model=List[Transaction])
def get_transactions():
    return db.get_transactions()

@app.post("/import", response_model=List[Transaction])
async def import_transactions(file: UploadFile = File(...)):
    # Save temporary file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        transactions_data = parse_csv(temp_path)
        imported_transactions = []
        for data in transactions_data:
            transaction_id = db.save_transaction(data)
            data["id"] = transaction_id
            imported_transactions.append(Transaction(**data))
        return imported_transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
