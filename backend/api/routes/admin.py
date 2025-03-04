"""
API routes for system administration tasks.
"""
import os
import json
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv, set_key, find_dotenv
from sentence_transformers import SentenceTransformer

# Import services
from search.chroma_store import get_collection_stats, reset_collection
from ingestion.document_processor import process_document

router = APIRouter()

# Load environment variables
load_dotenv()

# Models
class SystemStats(BaseModel):
    document_count: int
    total_chunks: int
    vector_store_size: str
    avg_query_time: float

class SystemConfig(BaseModel):
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    similarity_threshold: float

class SystemConfigUpdate(BaseModel):
    embedding_model: str = None
    chunk_size: int = None
    chunk_overlap: int = None
    similarity_threshold: float = None

@router.get("/admin/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get system statistics including document count, vector store size, etc.
    """
    try:
        # Get stats from ChromaDB
        stats = get_collection_stats()
        return stats
    except Exception as e:
        # If there's an error, return placeholder data
        print(f"Error getting system stats: {str(e)}")
        return {
            "document_count": 0,
            "total_chunks": 0,
            "vector_store_size": "0 MB",
            "avg_query_time": 0.0
        }

@router.get("/admin/config", response_model=SystemConfig)
async def get_system_config():
    """
    Get current system configuration.
    """
    return {
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "chunk_size": int(os.getenv("CHUNK_SIZE", "1000")),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200")),
        "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    }

@router.post("/admin/config", response_model=SystemConfig)
async def update_system_config(config_update: SystemConfigUpdate):
    """
    Update system configuration.
    """
    # Get current config
    current_config = await get_system_config()
    
    # Update environment variables
    env_file = find_dotenv()
    
    # Update only the values that are provided
    if config_update.embedding_model is not None:
        # Store the old model name for comparison
        old_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Update the environment variable
        set_key(env_file, "EMBEDDING_MODEL", config_update.embedding_model)
        current_config["embedding_model"] = config_update.embedding_model
        
        # Also update the global variable in the module
        import search.semantic_search
        search.semantic_search.MODEL_NAME = config_update.embedding_model
        
        # Reinitialize the embedding model if the model name has changed
        if old_model_name != config_update.embedding_model:
            try:
                model_path = config_update.embedding_model.split('/')[-1] if '/' in config_update.embedding_model else config_update.embedding_model
                search.semantic_search.embedding_model = SentenceTransformer(model_path)
                print(f"Reinitialized embedding model: {model_path}")
            except Exception as e:
                print(f"Error reinitializing embedding model: {str(e)}")
    
    if config_update.chunk_size is not None:
        set_key(env_file, "CHUNK_SIZE", str(config_update.chunk_size))
        current_config["chunk_size"] = config_update.chunk_size
        # Update the value in os.environ so it's available to other modules
        os.environ["CHUNK_SIZE"] = str(config_update.chunk_size)
    
    if config_update.chunk_overlap is not None:
        set_key(env_file, "CHUNK_OVERLAP", str(config_update.chunk_overlap))
        current_config["chunk_overlap"] = config_update.chunk_overlap
        # Update the value in os.environ so it's available to other modules
        os.environ["CHUNK_OVERLAP"] = str(config_update.chunk_overlap)
    
    if config_update.similarity_threshold is not None:
        set_key(env_file, "SIMILARITY_THRESHOLD", str(config_update.similarity_threshold))
        current_config["similarity_threshold"] = config_update.similarity_threshold
        # Update the value in os.environ so it's available to other modules
        os.environ["SIMILARITY_THRESHOLD"] = str(config_update.similarity_threshold)
    
    try:
        await apply_settings()
    except Exception as e:
        print(f"Warning: Failed to apply settings: {str(e)}")
    
    return current_config

@router.post("/admin/reindex")
async def reindex_documents(background_tasks: BackgroundTasks):
    """
    Trigger reindexing of all documents.
    """
    try:
        # Reset the vector database
        reset_collection()
        
        # Reprocess all documents in the uploads directory
        if os.path.exists("uploads") and os.path.isdir("uploads"):
            for filename in os.listdir("uploads"):
                file_path = os.path.join("uploads", filename)
                if os.path.isfile(file_path):
                    # Get document metadata from metadata directory if available
                    doc_id = os.path.splitext(filename)[0]
                    metadata_path = f"metadata/{doc_id}.json"
                    
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        
                        # Update status to processing
                        metadata["status"] = "processing"
                        
                        # Process document in background
                        background_tasks.add_task(process_document, file_path, metadata)
        
        return {"message": "Reindexing started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reindexing documents: {str(e)}")
    
@router.post("/admin/apply-settings")
async def apply_settings():
    """
    Apply current settings to the running application without restart.
    This is useful after updating configuration values.
    """
    try:
        # Reload environment variables
        load_dotenv(override=True)
        
        # Update semantic search module
        import search.semantic_search
        
        # Get the current values from environment
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
        
        # Reinitialize with current settings
        model_path = embedding_model.split('/')[-1] if '/' in embedding_model else embedding_model
        search.semantic_search.embedding_model = SentenceTransformer(model_path)
        search.semantic_search.MODEL_NAME = embedding_model
        
        # Ensure the module has the latest threshold value
        # This might require adding a global variable in semantic_search.py
        search.semantic_search.DEFAULT_THRESHOLD = threshold
        
        return {"message": "Settings applied successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying settings: {str(e)}")