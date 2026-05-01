import os
import argparse
from cpa_core.db import Database
from cpa_core.knowledge_base import KnowledgeBase

def ingest_document(file_path, db_path, model_path):
    # Initialize DB and KnowledgeBase
    db = Database(db_path)
    db.init_db()
    kb = KnowledgeBase(db)

    print(f"Ingesting {file_path} into KnowledgeBase...")
    try:
        doc_ids = kb.add_file(file_path)
        print(f"Successfully ingested {len(doc_ids)} chunks from {file_path}")
    except Exception as e:
        print(f"Error during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest tax documents into vector memory.")
    parser.add_argument("file_path", help="Path to the document (PDF, HTML, or TXT).")
    parser.add_argument("--db", default="cpa.db", help="Path to the SQLite database.")
    parser.add_argument("--model", default="models/Phi-3-mini-4k-instruct-q4.gguf", help="Path to the LLM model (for embedding generation).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        exit(1)
        
    ingest_document(args.file_path, args.db, args.model)
