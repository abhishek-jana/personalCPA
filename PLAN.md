# Personal Local CPA - Implementation Plan

## Objective
Build a completely local, privacy-first personal finance and tax management application. The system will ingest financial data locally, store it securely, and utilize a local LLM to provide tax categorization and reasoning based on ingested tax documents (RAG).

## Core Architecture
- **Intelligence Engine**: Local LLM via `llama.cpp` (taking advantage of 64GB RAM).
- **Data Storage & RAG**: SQLite, utilizing the `sqlite-vss` extension to store both relational financial data (transactions, accounts) and vector embeddings of tax documents.
- **Backend API**: Python FastAPI. This decoupled architecture allows multiple interfaces.
- **Interfaces**:
  - **Primary**: Local Web Application (e.g., React or Vue) served by FastAPI for rich data visualization and chat.
  - **Secondary**: Terminal CLI client for quick evaluations and rapid data entry.
- **Data Ingestion**: Manual upload/import of CSV/OFX/QFX files to maintain absolute privacy.
- **Tax Knowledge Updater**: A separate script/app responsible for scraping/downloading current tax codes and converting them into document embeddings for the SQLite vector database.

## Implementation Steps

### Phase 1: Core Backend & Database Setup
1. Initialize the Python project and FastAPI backend.
2. Setup the SQLite database with `sqlite-vss`.
3. Define the relational schema for `transactions`, `accounts`, and `categories`.
4. Implement the file parsing logic (CSV/OFX) to ingest transactions into the database.

### Phase 2: Local Intelligence (LLM Integration)
1. Integrate `llama.cpp` Python bindings.
2. Implement the text embedding pipeline using a lightweight local model.
3. Build the RAG retrieval pipeline: querying `sqlite-vss` to fetch relevant tax document chunks based on user prompts.
4. Create the core prompt templates for transaction categorization and tax advice.

### Phase 3: Interfaces
1. **CLI Client**: Build a basic Python CLI (using `Click` or `Typer`) that interacts with the FastAPI endpoints to query balances and import files.
2. **Web UI**: Develop a lightweight web frontend with charts for spending trends and a chat interface for the CPA assistant.

### Phase 4: Tax Knowledge Ingestion
1. Build the standalone script to process external tax documents (PDFs, HTML), chunk the text, generate embeddings, and insert them into the `sqlite-vss` database.

## Verification & Testing
- **Unit Tests**: Ensure the CSV/OFX parsers accurately extract data without loss.
- **Integration Tests**: Verify the FastAPI endpoints correctly interact with the SQLite database.
- **RAG Validation**: Test the vector similarity search to ensure relevant tax rules are retrieved based on sample queries.
- **Privacy Check**: Ensure the application attempts zero outbound network requests during standard operation.
