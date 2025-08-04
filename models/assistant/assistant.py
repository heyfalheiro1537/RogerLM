import os
import sys
from typing import List, Dict
from config import Config
from connection import check_ollama_connection

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

try:
    import requests
except ImportError:
    print("Requests not found. Installing...")
    os.system("pip install requests")
    import requests

# Configuration


class Assistant:
    def __init__(self, config: Config):
        self.config = config
        self.embedding_model = SentenceTransformer(config.config["embedding_model"])

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(config.db_path), settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.chroma_client.get_collection("documents")
        except:
            print(
                "No documents found. Please add documents first using --add-doc or --add-dir"
            )
            sys.exit(1)

    def search_documents(self, query: str, max_results: int = None) -> List[Dict]:
        """Search for relevant document chunks"""
        if max_results is None:
            max_results = self.config.config["max_results"]

        # Search in ChromaDB
        results = self.collection.query(query_texts=[query], n_results=max_results)

        # Format results
        formatted_results = []
        if results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                        if "distances" in results
                        else 0,
                    }
                )

        return formatted_results

    def query_ollama(self, prompt: str) -> str:
        """Query Ollama LLaMA model"""
        url = f"{self.config.config['ollama_url']}/api/generate"

        payload = {
            "model": self.config.config["model_name"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.config["temperature"],
                "num_predict": self.config.config["max_tokens"],
            },
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"
        except Exception as e:
            return f"Error processing response: {e}"

    def answer_question(self, question: str) -> str:
        """Answer question based on documents"""
        # Search for relevant documents
        relevant_docs = self.search_documents(question)

        if not relevant_docs:
            return "I couldn't find any relevant information in the documents to answer your question."

        # Prepare context from relevant documents
        context = "\n\n".join(
            [
                f"Document: {doc['metadata'].get('filename', 'Unknown')}\n{doc['content']}"
                for doc in relevant_docs
            ]
        )

        # Create prompt
        prompt = f"""Based ONLY on the following documents, answer the question. If the answer cannot be found in the provided documents, say "I cannot find this information in the provided documents."

Documents:
{context}

Question: {question}

Answer:"""

        # Query LLaMA
        response = self.query_ollama(prompt)

        # Add source information
        sources = list(
            set([doc["metadata"].get("filename", "Unknown") for doc in relevant_docs])
        )
        response += f"\n\nSources: {', '.join(sources)}"

        return response
