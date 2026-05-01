from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from cpa_core.db import Database
from cpa_core.ingest import parse_csv
from cpa_core.intelligence import CPAAssistant
from cpa_core.knowledge_base import KnowledgeBase
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

# Initialize KnowledgeBase
kb = KnowledgeBase(db)

# Initialize Assistant with Dependency Injection
MODEL_PATH = os.getenv("CPA_MODEL_PATH", "models/Phi-3-mini-4k-instruct-q4.gguf")
assistant = CPAAssistant(model_path=MODEL_PATH, kb=kb)

class Transaction(BaseModel):
    id: Optional[int] = None
    date: str
    description: str
    amount: float
    category: Optional[str] = None

class PulseResponse(BaseModel):
    tax_estimate: float
    savings_rate: str
    total_spent: float

class InboxAction(BaseModel):
    type: str
    message: str
    count: int

class ChatRequest(BaseModel):
    message: str
    use_rag: Optional[bool] = True

class ChatResponse(BaseModel):
    answer: str
    latency: float
    tokens: int
    tps: float

@app.get("/status")
def read_status():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/dashboard/pulse", response_model=PulseResponse)
def get_pulse():
    transactions = db.get_transactions()
    total_spent = sum(t["amount"] for t in transactions)
    return {
        "tax_estimate": 0.0,
        "savings_rate": "0%",
        "total_spent": total_spent
    }

@app.get("/dashboard/inbox", response_model=List[InboxAction])
def get_inbox():
    transactions = db.get_transactions()
    uncategorized = [t for t in transactions if t.get("category") is None]
    
    actions = []
    if uncategorized:
        actions.append({
            "type": "categorization",
            "message": f"Categorize {len(uncategorized)} transactions",
            "count": len(uncategorized)
        })
    
    return actions

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
        # High-leverage call: Assistant manages the RAG logic
        result = assistant.ask(request.message, use_rag=request.use_rag)
        return ChatResponse(
            answer=result.answer,
            latency=result.latency,
            tokens=result.tokens,
            tps=result.tps
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

class DocumentRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@app.post("/documents")
def add_document(request: DocumentRequest):
    doc_ids = kb.add_text(request.content)
    return {"ids": doc_ids, "status": "saved"}

@app.post("/search")
def search_documents(request: SearchRequest):
    return kb.query(request.query, limit=request.limit)
