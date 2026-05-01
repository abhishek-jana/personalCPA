# Project Summary: Personal Local CPA

## Current Project State (as of May 2026)
The Personal Local CPA is a privacy-first, offline financial assistant. It is currently in the implementation phase, with a functional core for transaction management, local LLM chat, and vector memory.

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Dependency Management**: [uv](https://astral.sh/uv)
- **Database**: SQLite with `sqlite-vss` extension (handling both relational and vector data).
- **Intelligence**: `llama-cpp-python` (v0.2.75) running **Phi-3 Mini** (GGUF).
- **Embeddings**: `fastembed` (BGE-small-en-v1.5) for local CPU-efficient vector generation.
- **Frontend**: Tailwind CSS + Vanilla JS (Single-page static app).
- **CLI**: Typer + Rich.

### Progress & Completed Slices
- [x] **Slice 1: Skeleton**: FastAPI server and Typer CLI established.
- [x] **Slice 2: Database**: SQLite-VSS persistence layer for transactions.
- [x] **Slice 3: Visual Spark**: Dashboard UI created (`frontend/index.html`).
- [x] **Slice 4: The Brains**: LLM integration complete. Interactive chat available via CLI and Web UI.
- [x] **Slice 5: Vector Memory**: Local text embedding pipeline and vector search integration complete.
- [x] **Slice 7: Bank Import**: Robust CSV parser implemented.

### Performance (Laptop Baseline)
- **Hardware**: i5-8350 CPU, 24GB RAM.
- **Model**: Phi-3-mini-4k-instruct-q4 (~2.4GB).
- **LLM Speed**: ~2.27 tokens per second (CPU-only).
- **Embedding Dim**: 384 (BGE-small).

### File Structure Highlights
- `/cpa_core`: Core modules for DB, Ingest, Intelligence, and Vector Search.
- `/data`: Local-only storage for bank statements and tax docs (ignored by Git).
- `/eval`: Evaluation suite with "Gold Standard" questions.
- `/models`: Storage for GGUF model files (ignored by Git).
- `install_llm.sh`: Dual-installation script for CPU (laptop) or GPU (beefy system).

## Resuming the Conversation
To continue work in a new session:
1. **Sync dependencies**: `uv sync`
2. **Start the backend**: `uv run python -m uvicorn main:app --reload`
3. **Trigger next slice**: Start with **Slice 6: RAG-based Tax Guru**.

### Goals for Slice 6
- Implement document ingestion script for large tax documents (PDF/HTML).
- Connection between vector search and the LLM chat assistant.
- Verification of grounded tax advice.
