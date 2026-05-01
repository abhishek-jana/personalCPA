import json
import time
import argparse
from typing import List, Dict
import os
from cpa_core.db import Database
from cpa_core.knowledge_base import KnowledgeBase
from cpa_core.intelligence import CPAAssistant

def load_gold_standard(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as f:
        return json.load(f)

def evaluate_model(model_path: str, gold_standard: List[Dict], db_path: str, use_rag: bool = False):
    print(f"Loading assistant with model: {model_path} (RAG: {'ON' if use_rag else 'OFF'})")
    
    # Initialize Core Components
    db = Database(db_path)
    db.init_db()
    kb = KnowledgeBase(db)
    assistant = CPAAssistant(model_path=model_path, kb=kb)

    results = []
    total_latency = 0
    total_tokens = 0

    for item in gold_standard:
        print(f"--- Running Test: {item['id']} ---")
        
        # Call the high-leverage ask interface
        result = assistant.ask(item['question'], use_rag=use_rag)
        
        total_latency += result.latency
        total_tokens += result.tokens
        
        # Simple accuracy check: keyword matching
        matched_keywords = [k for k in item['expected_answer_keywords'] if k.lower() in result.answer.lower()]
        accuracy_score = len(matched_keywords) / len(item['expected_answer_keywords'])
        
        print(f"Answer: {result.answer}")
        print(f"Latency: {result.latency:.2f}s | Tokens: {result.tokens} | TPS: {result.tps:.2f}")
        print(f"Accuracy (Keyword Match): {accuracy_score:.0%}")
        
        results.append({
            "id": item['id'],
            "latency": result.latency,
            "tokens": result.tokens,
            "tps": result.tps,
            "accuracy": accuracy_score,
            "answer": result.answer
        })

    avg_tps = total_tokens / total_latency if total_latency > 0 else 0
    avg_acc = sum(r['accuracy'] for r in results) / len(results)

    print("\n" + "="*30)
    print(f"FINAL EVALUATION REPORT (RAG: {'ON' if use_rag else 'OFF'})")
    print("="*30)
    print(f"Average TPS: {avg_tps:.2f}")
    print(f"Average Accuracy: {avg_acc:.0%}")
    print("="*30)

    db.close()
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a GGUF model using CPAAssistant.")
    parser.add_argument("model_path", type=str, help="Path to the GGUF model file.")
    parser.add_argument("--gold_standard", type=str, default="eval/gold_standard.json", help="Path to the gold standard questions.")
    parser.add_argument("--db", type=str, default="cpa.db", help="Path to the SQLite database.")
    parser.add_argument("--rag", action="store_true", help="Enable RAG during evaluation.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_path):
        print(f"Error: Model not found at {args.model_path}")
        exit(1)
        
    gold_standard = load_gold_standard(args.gold_standard)
    evaluate_model(args.model_path, gold_standard, args.db, use_rag=args.rag)
