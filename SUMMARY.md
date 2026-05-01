# Project Summary: Personal Local CPA

## Current Project State (as of May 2026)
The Personal Local CPA is a privacy-first, offline financial assistant. It is currently in the early implementation phase, with a functional core for transaction management and a basic local LLM chat interface.

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Dependency Management**: [uv](https://astral.sh/uv)
- **Database**: SQLite with `sqlite-vss` extension (handling both relational and vector data).
- **Intelligence**: `llama-cpp-python` (v0.2.75) running **Phi-3 Mini** (GGUF).
- **Frontend**: Tailwind CSS + Vanilla JS (Single-page static app).
- **CLI**: Typer + Rich.

### Progress & Completed Slices
- [x] **Slice 1: Skeleton**: FastAPI server and Typer CLI established with a "heartbeat" status.
- [x] **Slice 2: Database**: SQLite-VSS persistence layer for transactions.
- [x] **Slice 3: Visual Spark**: Dashboard UI created (`frontend/index.html`) to view transactions.
- [x] **Slice 4: The Brains**: LLM integration complete. Interactive chat available via CLI (`cpa chat`) and Web UI.
- [x] **Slice 7: Bank Import**: Robust CSV parser implemented to ingest real bank statements.

### Performance (Laptop Baseline)
- **Hardware**: i5-8350 CPU, 24GB RAM.
- **Model**: Phi-3-mini-4k-instruct-q4 (~2.4GB).
- **Speed**: ~2.27 tokens per second (CPU-only).

### File Structure Highlights
- `/cpa_core`: Core modules for DB, Ingest, and Intelligence.
- `/data`: Local-only storage for bank statements and tax docs (ignored by Git).
- `/eval`: Evaluation suite with "Gold Standard" questions for model benchmarking.
- `/models`: Storage for GGUF model files (ignored by Git).
- `install_llm.sh`: Dual-installation script for CPU (laptop) or GPU (beefy system).

## Resuming the Conversation
To continue work in a new session:
1. **Sync dependencies**: `uv sync`
2. **Start the backend**: `uv run python -m uvicorn main:app --reload`
3. **Trigger next slice**: Start with **Slice 5: Vector Memory**.

### Goals for Slice 5
- Implement text embedding pipeline (local model).
- Store embeddings in `sqlite-vss`.
- Implement vector search (top-k retrieval) for RAG.
