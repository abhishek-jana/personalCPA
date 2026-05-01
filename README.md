# Personal Local CPA

A completely local, privacy-first personal finance and tax management application.

## Overview
This application is designed for individuals who want the power of AI-driven financial advice without compromising their data privacy. It runs entirely on your local machine, using a local LLM and a local vector database.

## Features (Current)
- **FastAPI Backend**: A robust local server handling data and logic.
- **SQLite-VSS Database**: Relational storage for transactions + vector storage for tax knowledge.
- **CSV Ingestion**: Easily import bank statements without cloud syncing.
- **Rich CLI**: Manage your finances directly from the terminal.
- **Web Dashboard**: Simple, interactive visualization of your transactions.

## Tech Stack
- **Language**: Python 3.11+
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)
- **Framework**: FastAPI, Typer
- **Database**: SQLite with `sqlite-vss`
- **Frontend**: Tailwind CSS + Vanilla JS (currently a static single-page app)

## Getting Started

### Prerequisites
- Python 3.11 or higher.
- `uv` (Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup
1. Clone the repository.
2. Sync dependencies:
   ```bash
   uv sync
   ```

### Running the Application
1. **Start the Backend Server**:
   ```bash
   uv run python -m uvicorn main:app --reload
   ```
2. **Use the CLI**:
   ```bash
   # Check status
   uv run python cli.py status
   # List transactions
   uv run python cli.py list
   # Import a CSV
   uv run python cli.py import-csv data/bank_statements/sample.csv
   ```
3. **Open the Web UI**:
   Open `frontend/index.html` in your favorite web browser.

## Roadmap
- [x] Slice 1: Skeleton & CLI/API Connectivity
- [x] Slice 2: Database Persistence
- [x] Slice 3: Web Dashboard Scaffolding
- [ ] Slice 4: Local LLM Integration (Intelligence)
- [ ] Slice 5: Vector Memory & Embedding Pipeline
- [ ] Slice 6: RAG-based Tax Guru
- [x] Slice 7: Bank Statement Import Logic
