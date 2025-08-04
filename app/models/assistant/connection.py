import os
from models.config import Config

try:
    import requests
except ImportError:
    print("Requests not found. Installing...")
    os.system("pip install requests")
    import requests


def check_ollama_connection(config: Config) -> bool:
    """Check if Ollama is running and model is available"""
    try:
        # Check if Ollama is running
        response = requests.get(f"{config.config['ollama_url']}/api/tags", timeout=5)
        if response.status_code != 200:
            return False

        # Check if model is available
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]

        if config.config["model_name"] not in model_names:
            print(f"Model '{config.config['model_name']}' not found.")
            print("Available models:", model_names)
            print(f"Install the model with: ollama pull {config.config['model_name']}")
            return False

        return True
    except requests.exceptions.RequestException:
        print("Ollama is not running. Please start Ollama first.")
        print("Install Ollama from: https://ollama.ai")
        return False
