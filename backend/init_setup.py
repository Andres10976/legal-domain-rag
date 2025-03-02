"""
Initialization script to set up the necessary directories and configurations.
"""
import os
import json
import shutil

def init_directories():
    """Create all necessary directories."""
    directories = [
        "uploads",       # For uploaded documents
        "processed",     # For processed documents
        "vector_db",     # For vector database files
        "metadata",      # For document metadata
        "logs",          # For log files
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_empty_vector_db():
    """Create an empty vector database file."""
    vector_db_path = "vector_db/chunks.json"
    if not os.path.exists(vector_db_path):
        with open(vector_db_path, "w") as f:
            json.dump([], f)
        print(f"Created empty vector database: {vector_db_path}")

def check_environment():
    """Check if .env file exists, create from example if not."""
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example")
        print("Please edit .env with your actual API keys and configuration")

def main():
    """Main initialization function."""
    print("Initializing Legal Domain RAG System...")
    init_directories()
    create_empty_vector_db()
    check_environment()
    print("Initialization complete!")

if __name__ == "__main__":
    main()
