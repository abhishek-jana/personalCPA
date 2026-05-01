# ADR 0001: Architectural Deepening Candidates

## Status
Proposed

## Context
The initial implementation of Personal CPA followed a rapid "tracer bullet" approach. This resulted in several **shallow modules** and significant **coordination bloat** in the application layer (`main.py` and CLI). The system currently leaks implementation details about vector embeddings and database schemas across its seams.

## Proposed Candidates for Deepening

### 1. The `KnowledgeBase` Module
- **Files**: `cpa_core/db.py`, `cpa_core/intelligence.py`, `main.py`, `scripts/ingest_docs.py`
- **Problem**: Coordination bloat. Callers must manually orchestrate chunking, embedding, and saving.
- **Solution**: Create a `KnowledgeBase` module that encapsulates the `Embedder` and `Vector Store`.
- **Benefits**: Improved **Locality** and high **Leverage**. Callers use `add_text()` instead of managing vector dimensions.

### 2. Decoupling the `CPAAssistant`
- **Files**: `cpa_core/intelligence.py`
- **Problem**: Leaky seam. `rag_chat` is tightly coupled to the `Database` object.
- **Solution**: assistant consumes a generic `KnowledgeBase` interface.
- **Benefits**: Enables isolation testing and concentrates RAG orchestration logic.

### 3. Unifying the LLM Interface
- **Files**: `cpa_core/intelligence.py`, `eval/evaluator.py`
- **Problem**: Lack of locality. Evaluator re-implements LLM loading and prompting.
- **Solution**: Evaluator uses `CPAAssistant` as the single source of truth for LLM behavior.
- **Benefits**: Guarantees production-parity for benchmarks.

## Decision
The team has decided to proceed with **Candidate 1: The KnowledgeBase Module** first.
