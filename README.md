# Local LM Document Assistant

A command-line AI assistant that answers questions based exclusively on your local documents using LLaMA models via Ollama.

## Project Structure

```
RogerLM/
├── app/
│   ├── models/              # Core classes and components
│   │   ├── __init__.py      # Package initialization
│   │   ├── config.py        # Configuration management
│   │   ├── processor.py     # Document processing classes
│   │   └── assistant.py     # LLaMA assistant class
│   ├── main.py              # Main application entry point
│   ├── setup.py             # Installation script
│   └── requirements.txt     # Python dependencies
├── .gitignore               # Git ignore patterns
├── README.md                # This file
```

## Features

- **Document-only responses**: Only answers based on your uploaded documents
- **Multiple file formats**: Supports PDF, TXT, MD, DOC, DOCX
- **Vector search**: Uses ChromaDB for efficient document retrieval
- **Local processing**: Everything runs locally, no data sent to external services
- **Modular design**: Separated classes for better maintainability
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

### Step 3: Set up the project

1. **Clone or download the project**:
   ```bash
   git clone <your-repo-url>
   cd app
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the installer**:
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

### Quick Start

1. **Test the installation**:
   ```bash
   python main.py --help
   ```

2. **Add documents**:
   ```bash
   python main.py --add-doc /path/to/document.pdf
   # or add entire directory
   python main.py --add-dir /path/to/documents/
   ```

3. **Ask questions**:
   ```bash
   python main.py --query "What is this document about?"
   ```

4. **Interactive mode**:
   ```bash
   python main.py --interactive
   ```

### After Installation (CLI Commands)

Once installed via `setup.py`, you can use the `lm` command globally:

Add a single document:
```bash
lm --add-doc /path/to/document.pdf
```

```bash
lm --add-dir /path/to/documents/
```

Ask questions:
```bash
lm --query "What is the main topic of the documents?"
```

Start interactive mode:
```bash
lm --interactive
```

List processed documents:
```bash
lm --list-docs
```

### Configuration

View current configuration:
```bash
lm --config
```

Reset database (start fresh):
```bash
lm --reset
```

## Advanced Usage

### Supported File Types

- **PDF**: `.pdf`
- **Text**: `.txt`, `.md`
- **Word**: `.doc`, `.docx` (requires python-docx)

### Configuration Options

The assistant stores configuration in `~/.local_lm_assistant/config.json`:

```json
{
  "model_name": "llama2",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "max_results": 5,
  "ollama_url": "http://localhost:11434",
  "temperature": 0.1,
  "max_tokens": 500
}
```
## TODO
### Directory Structure (After Installation)

```
~/.local_lm_assistant/
├── config.json          # Configuration file
├── metadata.db          # SQLite database for document metadata
├── vector_db/           # ChromaDB vector database
└── logs/                # Application logs
```

## Development

### Project Architecture

- **main.py**: Entry point and CLI argument parsing
- **models/config.py**: Configuration management class
- **models/processor.py**: Document processing and vector database management
- **models/assistant.py**: LLaMA integration and question answering
- **setup.py**: Installation and system integration

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run directly
python main.py --add-doc test.pdf
python main.py --query "What is this about?"
```

### Creating Custom Models

You can extend the `models/` directory with additional classes:

```python
# models/custom_processor.py
from .processor import DocumentProcessor

class CustomProcessor(DocumentProcessor):
    def process_special_format(self, filepath):
        # Your custom processing logic
        pass
```

## Troubleshooting

### Common Issues

1. **"Ollama is not running"**
   - Make sure Ollama service is started: `ollama serve`
   - Check if running on different port in config

2. **"Model not found"**
   - Pull the model: `ollama pull llama2`
   - Check available models: `ollama list`

3. **"No documents found"**
   - Add documents first: `lm --add-doc /path/to/file.pdf`
   - Check processed documents: `lm --list-docs`

4. **Memory issues**
   - Use smaller model: `ollama pull llama2:7b`
   - Reduce chunk_size in config
   - Process fewer documents at once

### Logs

Check logs for detailed error information:
```bash
# View recent logs
tail -f ~/.local_lm_assistant/logs/assistant_$(date +%Y%m%d).log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes in the appropriate `models/` classes
4. Test thoroughly
5. Submit a pull request


## Support

- Check the logs in `~/.local_lm_assistant/logs/`
- Ensure Ollama is running and model is installed
- Verify documents are properly processed with `lm --list-docs`