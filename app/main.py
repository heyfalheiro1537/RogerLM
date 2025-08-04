#!/usr/bin/env python3
"""
Local LM Document Assistant
A CLI-based AI assistant that answers questions based only on provided documents
using LLaMA model via Ollama or transformers.
"""

import json
import argparse
import sqlite3
from pathlib import Path
from models.logging import Logger
from models.config import Config
from models.document_processor import DocumentProcessor


def main():
    parser = argparse.ArgumentParser(description="Local LM Document Assistant")
    parser.add_argument("--add-doc", help="Add a single document to the database")
    parser.add_argument("--add-dir", help="Add all documents from a directory")
    parser.add_argument("--query", "-q", help="Ask a question")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )
    parser.add_argument(
        "--list-docs", action="store_true", help="List processed documents"
    )
    parser.add_argument("--config", help="Show or update configuration")
    parser.add_argument(
        "--reset", action="store_true", help="Reset database and start fresh"
    )

    args = parser.parse_args()

    # Initialize configuration
    config = Config()
    Logger(config)

    # Handle reset
    if args.reset:
        import shutil

        if config.db_path.exists():
            shutil.rmtree(config.db_path)
        if config.sqlite_path.exists():
            config.sqlite_path.unlink()
        print("Database reset successfully.")
        return

    # Handle configuration
    if args.config:
        print("Current configuration:")
        print(json.dumps(config.config, indent=2))
        return

    # Initialize document processor
    processor = DocumentProcessor(config)

    # Handle document addition
    if args.add_doc:
        if not Path(args.add_doc).exists():
            print(f"File not found: {args.add_doc}")
            return
        chunks = processor.process_document(args.add_doc)
        print(f"Added {chunks} chunks to the database.")
        return

    if args.add_dir:
        if not Path(args.add_dir).exists():
            print(f"Directory not found: {args.add_dir}")
            return
        chunks = processor.process_directory(args.add_dir)
        print(f"Added {chunks} total chunks to the database.")
        return

    # Handle document listing
    if args.list_docs:
        conn = sqlite3.connect(config.sqlite_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename, filepath, processed_date, chunk_count FROM documents"
        )
        docs = cursor.fetchall()
        conn.close()

        if not docs:
            print("No documents processed yet.")
        else:
            print("Processed documents:")
            for doc in docs:
                print(f"  {doc[0]} ({doc[3]} chunks) - {doc[2]}")
        return

    # Check Ollama connection before querying
    if args.query or args.interactive:
        if not check_ollama_connection(config):
            return

    # Initialize assistant
    try:
        assistant = LLaMAAssistant(config)
    except SystemExit:
        return

    # Handle single query
    if args.query:
        answer = assistant.answer_question(args.query)
        print(f"\nQuestion: {args.query}")
        print(f"Answer: {answer}")
        return

    # Handle interactive mode
    if args.interactive:
        print("Local LM Document Assistant - Interactive Mode")
        print("Type 'quit' or 'exit' to stop, 'help' for commands")
        print("-" * 50)

        while True:
            try:
                question = input("\nYour question: ").strip()

                if question.lower() in ["quit", "exit"]:
                    break
                elif question.lower() == "help":
                    print("Commands:")
                    print("  help - Show this help")
                    print("  quit/exit - Exit interactive mode")
                    print("  Any other input - Ask a question")
                    continue
                elif not question:
                    continue

                print("Thinking...")
                answer = assistant.answer_question(question)
                print(f"\nAnswer: {answer}")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
        return

    # Show help if no arguments
    parser.print_help()


if __name__ == "__main__":
    main()
