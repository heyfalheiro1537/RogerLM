import os
import sqlite3
import hashlib
from pathlib import Path
from models.config import Config

# Core dependencies
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ChromaDB not found. Installing...")
    os.system("pip install chromadb")
    import chromadb
    from chromadb.config import Settings

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("SentenceTransformers not found. Installing...")
    os.system("pip install sentence-transformers")
    from sentence_transformers import SentenceTransformer

# Todo fix imports
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
except ImportError:
    print("LangChain not found. Installing...")
    os.system("pip install langchain pypdf")
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader, PyPDFLoader


# Configuration


class DocumentProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.config["chunk_size"],
            chunk_overlap=config.config["chunk_overlap"],
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(config.config["embedding_model"])

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(config.db_path), settings=Settings(anonymized_telemetry=False)
        )

        # Initialize SQLite for metadata
        self.init_sqlite()

    def init_sqlite(self):
        """Initialize SQLite database for document metadata"""
        conn = sqlite3.connect(self.config.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chunk_count INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def get_file_hash(self, filepath: str) -> str:
        """Generate hash for file to detect changes"""
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_document_processed(self, filepath: str) -> bool:
        """Check if document is already processed"""
        file_hash = self.get_file_hash(filepath)
        conn = sqlite3.connect(self.config.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def process_document(self, filepath: str) -> int:
        """Process a single document and add to vector database"""
        if self.is_document_processed(filepath):
            print(f"Document {filepath} already processed, skipping...")
            return 0

        print(f"Processing document: {filepath}")

        # Load document based on file type
        file_path = Path(filepath)
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(filepath)
        else:
            loader = TextLoader(filepath, encoding="utf-8")

        try:
            documents = loader.load()
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return 0

        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)

        if not texts:
            print(f"No text content found in {filepath}")
            return 0

        # Prepare data for ChromaDB
        collection_name = "documents"
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Document chunks for RAG"},
            )

        # Generate embeddings and add to collection
        chunk_texts = [doc.page_content for doc in texts]
        chunk_metadatas = []
        chunk_ids = []

        for i, doc in enumerate(texts):
            chunk_id = f"{file_path.stem}_{i}"
            chunk_ids.append(chunk_id)
            chunk_metadatas.append(
                {
                    "filename": file_path.name,
                    "filepath": str(file_path),
                    "chunk_index": i,
                    "source": str(file_path),
                }
            )

        # Add to ChromaDB
        collection.add(documents=chunk_texts, metadatas=chunk_metadatas, ids=chunk_ids)

        # Record in SQLite
        file_hash = self.get_file_hash(filepath)
        conn = sqlite3.connect(self.config.sqlite_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (filename, filepath, file_hash, chunk_count)
            VALUES (?, ?, ?, ?)
        """,
            (file_path.name, str(file_path), file_hash, len(texts)),
        )
        conn.commit()
        conn.close()

        print(f"Successfully processed {len(texts)} chunks from {filepath}")
        return len(texts)

    def process_directory(self, directory: str) -> int:
        """Process all documents in a directory"""
        total_chunks = 0
        directory_path = Path(directory)

        # Supported file types
        supported_extensions = {".txt", ".md", ".pdf", ".doc", ".docx"}

        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                chunks = self.process_document(str(file_path))
                total_chunks += chunks

        return total_chunks
