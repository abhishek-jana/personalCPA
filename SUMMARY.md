# Project Summary: Personal Local CPA

## Current Project State (as of May 2026)
The Personal Local CPA is a privacy-first, offline financial assistant. All initial roadmap slices are now complete. The application provides a full loop from data ingestion to AI-powered, document-grounded tax advice.

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Dependency Management**: [uv](https://astral.sh/uv)
- **Database**: SQLite with `sqlite-vss` extension.
- **Intelligence**: `llama-cpp-python` (v0.2.75) running **Phi-3 Mini**.
- **Embeddings**: `fastembed` (BGE-small-en-v1.5).
- **Document Processing**: `pypdf`, `beautifulsoup4`, `langchain-text-splitters`.
- **Frontend**: Tailwind CSS + Vanilla JS.
- **CLI**: Typer + Rich.

### Accomplishments (Roadmap Complete)
- [x] **Slice 1: Skeleton**: Project infrastructure established.
- [x] **Slice 2: Database**: Transaction persistence with SQLite.
- [x] **Slice 3: Visual Spark**: Interactive web dashboard.
- [x] **Slice 4: The Brains**: Local LLM chat integration.
- [x] **Slice 5: Vector Memory**: Local semantic search capability.
- [x] **Slice 6: Tax Guru (RAG)**: Document-grounded AI advice.
- [x] **Slice 7: Bank Import**: Automatic CSV parsing and normalization.

### How to use the RAG Assistant:
1. **Ingest your tax docs**:
   ```bash
   uv run python scripts/ingest_docs.py path/to/your/doc.pdf
   ```
2. **Ask questions**:
   ```bash
   uv run python cli.py chat --message "What is my tax bracket?"
   ```

## Next Steps & Future Enhancements
- **Multi-Year Analysis**: Compare tax liability across multiple years stored in `data/previous_years_tax`.
- **Chart Visualizations**: Add Plotly or Chart.js to the frontend for better spending analytics.
- **Improved Retrieval**: Implement re-ranking or hybrid search for even better tax advice.
- **Deployment**: Move to a beefier GPU system using `./install_llm.sh --gpu`.
