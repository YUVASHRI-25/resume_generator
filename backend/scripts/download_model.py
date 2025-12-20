import os
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, filename: str):
    """Download a file with progress bar."""
    print(f"Downloading {filename}...")
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Download the file with progress
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Get file size for progress bar
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(filename, 'wb') as f, tqdm(
        desc=os.path.basename(filename),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            size = f.write(data)
            bar.update(size)
    
    print(f"Successfully downloaded {filename}")

def download_mistral_model():
    """Download the Mistral 7B GGUF model."""
    # Model details
    model_name = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    model_url = f"https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/{model_name}"
    
    # Create models directory
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Download the model
    model_path = models_dir / model_name
    if not model_path.exists():
        download_file(model_url, str(model_path))
    else:
        print(f"Model already exists at: {model_path}")
    
    return str(model_path)

if __name__ == "__main__":
    model_path = download_mistral_model()
    print(f"Model is ready at: {model_path}")
