"""
Semantic search module.

Handles the conversion of queries to embeddings and retrieval of relevant documents.
"""
import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import ChromaDB store
from search.chroma_store import query_documents as chroma_query

# Load environment variables
load_dotenv()

# Initialize embedding model
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
try:
    # Extract model name without sentence-transformers/ prefix if present
    model_path = MODEL_NAME.split('/')[-1] if '/' in MODEL_NAME else MODEL_NAME
    embedding_model = SentenceTransformer(model_path)
    print(f"Initialized embedding model: {model_path}")
except Exception as e:
    print(f"Error loading embedding model: {str(e)}")
    print("Using backup model: all-MiniLM-L6-v2")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text using Sentence Transformers.
    
    Args:
        text: The input text to embed
        
    Returns:
        Embedding vector as a list of floats
    """
    # Generate embedding
    embedding = embedding_model.encode(text)
    
    # Convert to list of floats
    return embedding.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score
    """
    # Convert to numpy arrays for easier computation
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    
    return dot_product / (norm_vec1 * norm_vec2)

def keyword_match_score(query: str, text: str) -> float:
    """
    Calculate a simple keyword match score.
    
    Args:
        query: The search query
        text: The document text
        
    Returns:
        Keyword match score between 0 and 1
    """
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    
    if not query_words:
        return 0.0
    
    matches = query_words.intersection(text_words)
    return len(matches) / len(query_words)

def apply_filters(chunks: List[Dict], filters: Dict) -> List[Dict]:
    """
    Apply filters to chunks based on metadata.
    
    Args:
        chunks: List of document chunks
        filters: Dictionary of filters (e.g., {"jurisdiction": "California"})
        
    Returns:
        Filtered list of chunks
    """
    if not filters:
        return chunks
    
    filtered_chunks = []
    for chunk in chunks:
        match = True
        for key, value in filters.items():
            if key in chunk["metadata"] and chunk["metadata"][key] != value:
                match = False
                break
        if match:
            filtered_chunks.append(chunk)
    
    return filtered_chunks

def retrieve_relevant_chunks(
    query: str, 
    filters: Optional[Dict] = None, 
    top_k: int = 5, 
    threshold: float = 0.3
) -> List[Dict]:
    """
    Retrieve relevant document chunks based on query and filters.
    
    Args:
        query: The search query
        filters: Dictionary of metadata filters
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of relevant chunks with similarity scores
    """
    try:
        # Use ChromaDB to retrieve relevant chunks
        results = chroma_query(
            query_text=query,
            filters=filters,
            top_k=top_k,
            threshold=threshold
        )
        
        return results
        
    except Exception as e:
        print(f"Error retrieving chunks from ChromaDB: {str(e)}")
        # Return empty list in case of error
        return []
