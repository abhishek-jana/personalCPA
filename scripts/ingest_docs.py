import os
import argparse
from pypdf import PdfReader
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from cpa_core.db import Database
from cpa_core.intelligence import CPAAssistant

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        return soup.get_text()

def ingest_document(file_path, db_path, model_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in [".html", ".htm"]:
        text = extract_text_from_html(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print(f"Unsupported file type: {ext}")
        return

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    print(f"Split document into {len(chunks)} chunks.")

    # Initialize DB and Assistant
    db = Database(db_path)
    db.init_db()
    assistant = CPAAssistant(model_path)

    # Process and save chunks
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        print(f"Ingesting chunk {i+1}/{len(chunks)}...", end="\r")
        embedding = assistant.embed(chunk)
        db.save_document(chunk, embedding)
    
    print(f"\nSuccessfully ingested {file_path}")
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
