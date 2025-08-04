# Local LM Document Assistant

A command-line AI assistant that answers questions based exclusively on your local documents using LLaMA models via Ollama.

## Features

- **Document-only responses**: Only answers based on your uploaded documents
- **Multiple file formats**: Supports PDF, TXT, MD, DOC, DOCX
- **Vector search**: Uses ChromaDB for efficient document retrieval
- **Local processing**: Everything runs locally, no data sent to external services
- **CLI interface**: Simple command-line interface
- **Interactive mode**: Chat-like experience for multiple questions

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** for running LLaMA models locally

## Installation

### Step 1: Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and follow the installation instructions for your platform.

Or use the quick install script:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Pull a LLaMA model

```bash
# For LLaMA 2 (7B parameters - recommended for most users)
ollama pull llama2:7b

# For full LLaMA 2 (13B parameters - better quality, requires more RAM)
ollama pull llama2

# For smaller/faster model
ollama pull llama2:chat
```

### Step 3: Install the Assistant

1. **Download the files**:
   - `local_lm_assistant.py` (main application)
   - `setup.py` (installer)
   - `requirements.txt` (dependencies)

2. **Run the installer**:
   ```bash
   python setup.py
   ```

This will:
- Install all required Python dependencies
- Create the `lm` command in your system
- Set up the necessary directories
- Show you next steps

### Step 4: Start Ollama service

```bash
ollama serve
```

Keep this running in a terminal tab/window.

## Usage

### Add Documents

Add a single document:
```bash
lm --add-doc /path/to/document.pdf
```

Add all documents from a directory: