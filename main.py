from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from cpa_core.db import Database
from cpa_core.ingest import parse_csv
from cpa_core import intelligence
from cpa_core.knowledge_base import KnowledgeBase
from cpa_core.health import SystemHealth
from cpa_core.watcher import start_watcher
import os
import shutil
import asyncio

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

# Start Filesystem Watcher
kb.sync()
watcher = start_watcher(kb)

# Model Definitions based on user hardware (8GB VRAM / 64GB RAM)
MODELS = {
    "painless": os.getenv("CPA_MODEL_PAINLESS", "llama3.1:8b-instruct-q8_0"),
    "intelligence": os.getenv("CPA_MODEL_INTELLIGENCE", "mistral-nemo"),
    "fast": "phi3"
}

# Initial State
LLM_BACKEND = os.getenv("CPA_LLM_BACKEND", "ollama").lower()
SELECTED_MODEL_KEY = os.getenv("CPA_MODEL_TYPE", "painless").lower()

health_checker = SystemHealth(ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"))

@app.get("/health")
def get_health():
    current_model = MODELS.get(SELECTED_MODEL_KEY, MODELS["painless"])
    return health_checker.run_all(
        critical_models=[current_model], 
        optional_models=list(MODELS.values())
    )

def create_provider(backend: str, model_key: str):
    model_name = MODELS.get(model_key, MODELS["painless"])
    if backend == "ollama":
        OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
        return intelligence.OllamaProvider(model_name=model_name, base_url=OLLAMA_URL)
    else:
        MODEL_PATH = os.getenv("CPA_MODEL_PATH", "models/Phi-3-mini-4k-instruct-q4.gguf")
        GPU_LAYERS = int(os.getenv("CPA_GPU_LAYERS", "0"))
        return intelligence.LlamaCppProvider(model_path=MODEL_PATH, n_gpu_layers=GPU_LAYERS)

# Global Assistant Instance
current_provider = create_provider(LLM_BACKEND, SELECTED_MODEL_KEY)
assistant = intelligence.CPAAssistant(provider=current_provider, kb=kb)
auditor = intelligence.CPAAuditor(provider=current_provider, kb=kb)

@app.get("/config")
def get_config():
    # Helper to get current model name from provider
    model_name = "unknown"
    if hasattr(assistant.provider, "model_name"):
        model_name = assistant.provider.model_name
    elif hasattr(assistant.provider, "llm"):
        model_name = os.path.basename(assistant.provider.llm.model_path)

    return {
        "backend": LLM_BACKEND,
        "model": model_name,
        "model_type": SELECTED_MODEL_KEY,
        "available_types": list(MODELS.keys())
    }

class ModelSwitchRequest(BaseModel):
    model_type: str

@app.post("/config/model")
def switch_model(request: ModelSwitchRequest):
    global SELECTED_MODEL_KEY
    
    if request.model_type not in MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model type. Available: {list(MODELS.keys())}")
    
    SELECTED_MODEL_KEY = request.model_type
    new_model_name = MODELS[SELECTED_MODEL_KEY]
    
    # Hot-swap for Ollama (just change the string)
    if isinstance(assistant.provider, intelligence.OllamaProvider):
        assistant.provider.model_name = new_model_name
    else:
        # Cold-swap for llama-cpp (requires re-initialization of the C++ object)
        assistant.provider = create_provider(LLM_BACKEND, SELECTED_MODEL_KEY)
        
    return {
        "status": "switched", 
        "new_type": SELECTED_MODEL_KEY, 
        "new_model": new_model_name
    }

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
    collection: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    latency: float
    tokens: int
    tps: float
    collection_used: Optional[str] = None

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
    
    # Logic to show audit alerts (simplified for demo)
    # Only checks if no other actions are pending
    if not actions:
        collections = kb.get_collections()
        for col in collections:
            # We don't want to block the dashboard load, but for small local use this is okay
            # A real app would use a cached anomaly table updated by a background task
            anomalies = auditor.audit_collection(col)
            if anomalies:
                actions.append({
                    "type": "audit",
                    "message": f"{len(anomalies)} miscategorized documents in {col}",
                    "count": len(anomalies)
                })
                break 

    return actions

@app.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction):
    transaction_id = db.save_transaction(transaction.model_dump())
    transaction.id = transaction_id
    return transaction

@app.get("/transactions", response_model=List[Transaction])
def get_transactions():
    return db.get_transactions()

@app.post("/transactions/categorize")
def categorize_all():
    uncategorized = db.get_uncategorized_transactions()
    if not uncategorized:
        return {"status": "no transactions to categorize"}
    
    # Process through Assistant
    categorized = assistant.categorize_transactions(uncategorized)
    
    # Save back to DB
    for t in categorized:
        db.update_transaction(t["id"], {"category": t["category"]})
        
    return {"status": "success", "count": len(categorized)}

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
        result = assistant.ask(request.message, use_rag=request.use_rag, collection=request.collection)
        return ChatResponse(
            answer=result.answer,
            latency=result.latency,
            tokens=result.tokens,
            tps=result.tps,
            collection_used=result.collection_used
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

class DocumentRequest(BaseModel):
    content: str
    collection: Optional[str] = "default"

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    collection: Optional[str] = None

@app.get("/collections")
def list_collections():
    return kb.get_collections()

class CreateCollectionRequest(BaseModel):
    name: str

@app.post("/collections")
def create_collection(request: CreateCollectionRequest):
    kb.add_collection(request.name)
    # Ensure physical directory exists
    collection_path = os.path.join("data/collections", request.name)
    if not os.path.exists(collection_path):
        os.makedirs(collection_path)
    return {"status": "created", "name": request.name}

@app.get("/collections/{collection_name}/documents")
def list_collection_documents(collection_name: str):
    return kb.get_documents_in_collection(collection_name)

@app.post("/documents")
def add_document(request: DocumentRequest):
    doc_ids = kb.add_text(request.content, collection=request.collection)
    return {"ids": doc_ids, "status": "saved"}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), collection: str = Form(...)):
    collection_dir = os.path.join("data/collections", collection)
    if not os.path.exists(collection_dir):
        os.makedirs(collection_dir)
        
    file_path = os.path.join(collection_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        kb.sync() 
        return {"status": "ingested", "collection": collection, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/search")
def search_documents(request: SearchRequest):
    return kb.query(request.query, limit=request.limit, collection=request.collection)

@app.post("/audit/{collection_name}")
def run_audit(collection_name: str):
    return auditor.audit_collection(collection_name)

class MoveDocumentRequest(BaseModel):
    filename: str
    from_collection: str
    to_collection: str

@app.post("/documents/move")
def move_document(request: MoveDocumentRequest):
    old_path = os.path.join("data/collections", request.from_collection, request.filename)
    new_dir = os.path.join("data/collections", request.to_collection)
    new_path = os.path.join(new_dir, request.filename)
    
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        kb.sync()
        return {"status": "moved", "filename": request.filename}
    else:
        raise HTTPException(status_code=404, detail="File not found on disk")

# Serve Frontend Assets
frontend_path = os.path.join(os.getcwd(), "frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Fallback to index.html for SPA routing
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    print(f"Warning: Frontend assets not found at {frontend_path}. UI will not be served.")
