import json
import time
import argparse
from typing import List, Dict
from llama_cpp import Llama
import os

def load_gold_standard(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as f:
        return json.load(f)

def evaluate_model(model_path: str, gold_standard: List[Dict]):
    print(f"Loading model: {model_path}")
    # Load model with reasonable defaults for a 24GB laptop
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=os.cpu_count(),
        verbose=False
    )

    results = []
    total_latency = 0
    total_tokens = 0

    for item in gold_standard:
        print(f"--- Running Test: {item['id']} ---")
        prompt = f"Q: {item['question']}\nA:"
        
        start_time = time.time()
        # Generate response
        response = llm(
            prompt,
            max_tokens=256,
            stop=["Q:", "\n"],
            echo=False
        )
        end_time = time.time()
        
        latency = end_time - start_time
        answer = response['choices'][0]['text'].strip()
        usage = response['usage']
        completion_tokens = usage['completion_tokens']
        
        total_latency += latency
        total_tokens += completion_tokens
        
        # Simple accuracy check: keyword matching
        matched_keywords = [k for k in item['expected_answer_keywords'] if k.lower() in answer.lower()]
        accuracy_score = len(matched_keywords) / len(item['expected_answer_keywords'])
        
        print(f"Answer: {answer}")
        print(f"Latency: {latency:.2f}s | Tokens: {completion_tokens} | TPS: {completion_tokens/latency:.2f}")
        print(f"Accuracy (Keyword Match): {accuracy_score:.0%}")
        
        results.append({
            "id": item['id'],
            "latency": latency,
            "tokens": completion_tokens,
            "tps": completion_tokens / latency if latency > 0 else 0,
            "accuracy": accuracy_score,
            "answer": answer
        })

    avg_tps = total_tokens / total_latency if total_latency > 0 else 0
    avg_acc = sum(r['accuracy'] for r in results) / len(results)

    print("\n" + "="*30)
    print("FINAL EVALUATION REPORT")
    print("="*30)
    print(f"Average TPS: {avg_tps:.2f}")
    print(f"Average Accuracy: {avg_acc:.0%}")
    print("="*30)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a GGUF model on financial/tax questions.")
    parser.add_argument("model_path", type=str, help="Path to the GGUF model file.")
    parser.add_argument("--gold_standard", type=str, default="eval/gold_standard.json", help="Path to the gold standard questions.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_path):
        print(f"Error: Model not found at {args.model_path}")
        exit(1)
        
    gold_standard = load_gold_standard(args.gold_standard)
    evaluate_model(args.model_path, gold_standard)
