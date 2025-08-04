import json
from pathlib import Path


class Config:
    def __init__(self):
        self.app_dir = Path.home() / ".local_lm_assistant"
        self.db_path = self.app_dir / "vector_db"
        self.sqlite_path = self.app_dir / "metadata.db"
        self.config_path = self.app_dir / "config.json"
        self.logs_path = self.app_dir / "logs"

        # Default settings
        self.default_config = {
            "model_name": "llama2",  # Ollama model name
            "embedding_model": "all-MiniLM-L6-v2",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "max_results": 5,
            "ollama_url": "http://localhost:11434",
            "temperature": 0.1,
            "max_tokens": 500,
        }

        self.ensure_directories()
        self.load_config()

    def ensure_directories(self):
        """Create necessary directories"""
        self.app_dir.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config.copy()
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
