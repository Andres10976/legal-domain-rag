"""
ChromaDB vector database integration for document storage and retrieval.

ChromaDB is an open-source embedding database that can run locally with no additional costs.
"""
import os
import json
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Default path for ChromaDB persistence
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vector_db/chroma")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# Use all-MiniLM-L6-v2 embedding function from Sentence Transformers as default
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def initialize_collection():
    """
    Initialize or get the ChromaDB collection for document storage.
    """
    # Create collection if it doesn't exist, otherwise get the existing one
    try:
        collection = client.get_collection(name="legal_documents", embedding_function=default_ef)
        print(f"Retrieved existing collection 'legal_documents'")
    except Exception:
        collection = client.create_collection(name="legal_documents", embedding_function=default_ef)
        print(f"Created new collection 'legal_documents'")
    
    return collection

def add_documents(chunks: List[Dict]):
    """
    Add document chunks to the vector database.
    
    Args:
        chunks: List of document chunks with embeddings
    """
    collection = initialize_collection()
    
    # Format data for ChromaDB
    ids = [chunk["chunk_id"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = []
    
    for chunk in chunks:
        # Extract and format metadata for ChromaDB
        metadata = {
            "document_id": chunk["document_id"],
            "document_title": chunk["document_title"]
        }
        
        # Add additional metadata if available
        if "metadata" in chunk and chunk["metadata"]:
            for key, value in chunk["metadata"].items():
                if key not in ["id", "filename"] and value is not None:
                    metadata[key] = value
        
        metadatas.append(metadata)
    
    # Add data to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Added {len(chunks)} document chunks to ChromaDB")

def query_documents(
    query_text: str,
    filters: Optional[Dict] = None,
    top_k: int = 5,
    threshold: float = 0.3
) -> List[Dict]:
    """
    Query the vector database for relevant document chunks.
    
    Args:
        query_text: The query text
        filters: Optional metadata filters
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of relevant document chunks with similarity scores
    """
    collection = initialize_collection()
    
    # Format filters for ChromaDB if provided
    where_clause = {}
    if filters:
        for key, value in filters.items():
            where_clause[key] = value
    
    # Query the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k * 2,  # Get more results than needed for post-filtering
        where=where_clause if where_clause else None
    )

    # Format results
    chunks = []
    for i in range(len(results["ids"][0])):
        # Calculate normalized similarity score
        distance = results["distances"][0][i] if "distances" in results else 0.5
        # For distance-based similarity, convert to similarity score (1 - normalized distance)
        similarity_score = 1.0 / (1.0 + distance)  # Always between 0 and 1
        
        # Only include results above threshold
        if similarity_score >= threshold:
            chunks.append({
                "chunk_id": results["ids"][0][i],
                "document_id": results["metadatas"][0][i]["document_id"],
                "document_title": results["metadatas"][0][i]["document_title"],
                "text": results["documents"][0][i],
                "score": similarity_score
            })
    
    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]

def delete_document(document_id: str) -> bool:
    """
    Delete all chunks associated with a document from the vector database.
    
    Args:
        document_id: The ID of the document to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = initialize_collection()
        collection.delete(where={"document_id": document_id})
        print(f"Deleted document {document_id} from ChromaDB")
        return True
    except Exception as e:
        print(f"Error deleting document from ChromaDB: {str(e)}")
        return False

def get_collection_stats() -> Dict:
    """
    Get statistics about the vector database collection.
    
    Returns:
        Dictionary with collection statistics
    """
    collection = initialize_collection()
    
    # Count unique documents
    results = collection.get()
    
    # Get unique document IDs
    document_ids = set()
    if results and "metadatas" in results and results["metadatas"]:
        for metadata in results["metadatas"]:
            if metadata and "document_id" in metadata:
                document_ids.add(metadata["document_id"])
    
    return {
        "document_count": len(document_ids),
        "total_chunks": collection.count(),
        "vector_store_size": "Unknown",  # ChromaDB doesn't easily expose size info
        "avg_query_time": 0.0  # Would need benchmarking
    }

def reset_collection() -> bool:
    """
    Reset the vector database collection (delete all documents).
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = initialize_collection()
        collection.delete(where={})
        print("Reset ChromaDB collection")
        return True
    except Exception as e:
        print(f"Error resetting ChromaDB collection: {str(e)}")
        return False
