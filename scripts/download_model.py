import requests
import os
import argparse
from tqdm import tqdm

def download_file(url: str, dest_path: str):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    
    with open(dest_path, 'wb') as file, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(dest_path)
    ) as progress_bar:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

if __name__ == "__main__":
    MODELS = {
        "phi3-mini": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
        "llama3-8b": "https://huggingface.co/MaziyarPanahi/Llama-3-8B-Instruct-v0.1-GGUF/resolve/main/Llama-3-8B-Instruct-v0.1.Q4_K_M.gguf"
    }

    parser = argparse.ArgumentParser(description="Download GGUF models from Hugging Face.")
    parser.add_argument("model_name", choices=MODELS.keys(), help="Name of the model to download.")
    parser.add_argument("--output_dir", default="models", help="Directory to save the model.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    model_url = MODELS[args.model_name]
    filename = os.path.basename(model_url)
    dest_path = os.path.join(args.output_dir, filename)
    
    if os.path.exists(dest_path):
        print(f"Model already exists at {dest_path}")
    else:
        print(f"Downloading {args.model_name} from {model_url}...")
        download_file(model_url, dest_path)
        print(f"Download complete: {dest_path}")
