# Context: Personal Local CPA

## Overview
A completely local, privacy-first personal finance and tax management application.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite with `sqlite-vss` (relational + vector)
- **LLM**: `llama-cpp-python` (Llama.cpp)
- **UI**: Web (React/Vue) + CLI (Typer)

## Domain Language
- **Transaction**: A single financial record (income or expense).
- **RAG**: Retrieval-Augmented Generation, used to ground LLM tax advice in real documents.
- **CPA Assistant**: The AI-powered component providing tax and financial advice.

## Current State
- Initial implementation plan established in `PLAN.md`.
- Repository initialized and pushed to GitHub.
- Agent skills configuration complete.
