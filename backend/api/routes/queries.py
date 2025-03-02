"""
API routes for handling queries and generating responses.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
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
    similarity_threshold: Optional[float] = 0.7

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

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Process a natural language query against the document corpus.
    Returns a response with citations to source documents.
    """
    try:
        # Retrieve relevant document chunks
        chunks = retrieve_relevant_chunks(
            query=request.query,
            filters=request.filters,
            top_k=request.chunk_count,
            threshold=request.similarity_threshold
        )
        
        if not chunks:
            return {
                "query": request.query,
                "response": "I couldn't find any relevant information in the documents to answer your question.",
                "citations": [],
                "confidence_score": 0.0
            }
        
        # Assemble context from chunks
        context = assemble_context(chunks)
        
        # Generate response using LLM
        response, confidence = generate_response(request.query, context)
        
        # Format citations
        citations = []
        for chunk in chunks:
            citations.append({
                "document_id": chunk["document_id"],
                "document_title": chunk["document_title"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"][:200] + "...",  # Truncate for display
                "relevance_score": chunk["score"]
            })
        
        return {
            "query": request.query,
            "response": response,
            "citations": citations,
            "confidence_score": confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/history", response_model=ConversationHistory)
async def get_history():
    """
    Retrieve conversation history for the current session.
    In a real implementation, this would be tied to user sessions.
    """
    # This is a placeholder - in a real implementation, this would query a database
    # and be linked to the user's session
    return {
        "history": [
            # Sample history items would come from a database
        ]
    }
