"""
Updated get_history function and query_documents function in backend/api/routes/queries.py
"""
# Add these imports at the top of the file
import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi import HTTPException
from pydantic import BaseModel

# Import services
from search.semantic_search import retrieve_relevant_chunks
from context.context_assembly import assemble_context
from llm.response_generator import generate_response

router = APIRouter()


# Models
class QueryRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    chunk_count: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.3

class Citation(BaseModel):
    document_id: str
    document_title: str
    chunk_id: str
    text: str
    relevance_score: float

class QueryResponse(BaseModel):
    query: str
    response: str
    citations: List[Citation]
    confidence_score: float

class HistoryItem(BaseModel):
    query: str
    response: str
    timestamp: str

class ConversationHistory(BaseModel):
    history: List[HistoryItem]

# Add a helper function to save history
def save_to_history(query_data, response_data):
    """
    Save a query and response to history file.
    """
    history_dir = "query_history"
    os.makedirs(history_dir, exist_ok=True)
    
    history_file = os.path.join(history_dir, "history.json")
    
    # Load existing history or create new
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except:
            history = {"history": []}
    else:
        history = {"history": []}
    
    # Add new entry to history
    history_item = {
        "query": query_data.query,
        "response": response_data["response"],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to start of list (most recent first)
    history["history"].insert(0, history_item)
    
    # Keep only the last 20 items
    history["history"] = history["history"][:20]
    
    # Save back to file
    with open(history_file, "w") as f:
        json.dump(history, f)

@router.get("/history", response_model=ConversationHistory)
async def get_history():
    """
    Retrieve conversation history for the current session.
    """
    history_dir = "query_history"
    history_file = os.path.join(history_dir, "history.json")
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {str(e)}")
    
    # Return empty history if file doesn't exist or there's an error
    return {"history": []}

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Process a natural language query against the document corpus.
    Returns a response with citations to source documents.
    """
    try:
        # Force-read current similarity threshold from environment
        env_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
        
        # Log the values for debugging
        print(f"Query requested threshold: {request.similarity_threshold}, Env threshold: {env_threshold}")
        
        # Prioritize environment threshold over request default
        actual_threshold = env_threshold
        
        # Retrieve relevant document chunks with environment threshold
        chunks = retrieve_relevant_chunks(
            query=request.query,
            filters=request.filters,
            top_k=request.chunk_count,
            threshold=actual_threshold
        )
        
        if not chunks:
            response_data = {
                "query": request.query,
                "response": "I couldn't find any relevant information in the documents to answer your question.",
                "citations": [],
                "confidence_score": 0.0
            }
            # Save to history
            save_to_history(request, response_data)
            return response_data
        
        # Assemble context from chunks
        context = assemble_context(chunks)
        
        # Generate response using LLM
        response, confidence = generate_response(request.query, context)
        
        # Format citations with more complete text
        citations = []
        for chunk in chunks:
            citations.append({
                "document_id": chunk["document_id"],
                "document_title": chunk["document_title"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],  # Include full text instead of truncated version
                "relevance_score": chunk["score"]
            })
        
        response_data = {
            "query": request.query,
            "response": response,
            "citations": citations,
            "confidence_score": confidence
        }
        
        # Save to history
        save_to_history(request, response_data)
        
        return response_data
        
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)