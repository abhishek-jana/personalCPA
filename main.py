from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from cpa_core.db import Database
from cpa_core.ingest import parse_csv
from cpa_core.intelligence import CPAAssistant
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

# Initialize Assistant
MODEL_PATH = os.getenv("CPA_MODEL_PATH", "models/Phi-3-mini-4k-instruct-q4.gguf")
assistant = CPAAssistant(model_path=MODEL_PATH)

class Transaction(BaseModel):
    id: Optional[int] = None
    date: str
    description: str
    amount: float
    category: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = assistant.chat(request.message)
        return ChatResponse(answer=answer)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

class DocumentRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@app.post("/documents")
def add_document(request: DocumentRequest):
    embedding = assistant.embed(request.content)
    doc_id = db.save_document(request.content, embedding)
    return {"id": doc_id, "status": "saved"}

@app.post("/search")
def search_documents(request: SearchRequest):
    query_embedding = assistant.embed(request.query)
    results = db.search_documents(query_embedding, limit=request.limit)
    return results
