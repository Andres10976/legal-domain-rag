"""
Context assembly module.

Handles the assembly of retrieved chunks into coherent context for the LLM.
"""
from typing import List, Dict, Any

def assemble_context(chunks: List[Dict]) -> Dict:
    """
    Assemble retrieved chunks into coherent context for the LLM.
    
    This function:
    1. Sorts chunks by relevance score
    2. Combines chunk text
    3. Adds source attribution
    4. Handles context window limitations
    5. Resolves potential contradictions
    
    Args:
        chunks: List of document chunks with relevance scores
        
    Returns:
        Assembled context with source attribution
    """
    if not chunks:
        return {"text": "", "sources": []}
    
    # Sort chunks by relevance score (descending)
    sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
    
    # Extract document metadata for source attribution
    sources = []
    for chunk in sorted_chunks:
        source = {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "document_title": chunk["document_title"],
            "relevance_score": chunk["score"]
        }
        if source not in sources:
            sources.append(source)
    
    # Prepare context text with source attribution
    context_parts = []
    for i, chunk in enumerate(sorted_chunks):
        # Add source reference
        source_ref = f"[Source {i+1}: {chunk['document_title']}]"
        
        # Add chunk text with source reference
        context_parts.append(f"{source_ref}\n{chunk['text']}\n")
    
    # Combine all parts into a single context text
    context_text = "\n".join(context_parts)
    
    # If context is too long, we would implement summarization or filtering
    # This is a simplified implementation - in a real system, we would handle
    # context window limitations more intelligently
    max_context_length = 10000  # Placeholder value
    if len(context_text) > max_context_length:
        # Simple truncation strategy - in a real system, we would use more sophisticated methods
        context_text = context_text[:max_context_length] + "..."
    
    return {
        "text": context_text,
        "sources": sources
    }

def handle_contradictions(chunks: List[Dict]) -> List[Dict]:
    """
    Detect and resolve contradictory information in chunks.
    
    In a real implementation, this would use more sophisticated methods
    to identify and resolve contradictions.
    
    Args:
        chunks: List of document chunks
        
    Returns:
        List of chunks with contradictions resolved
    """
    # This is a placeholder implementation
    # In a real system, we would implement more sophisticated contradiction detection
    # For example, using sentence similarity, named entity recognition, etc.
    
    # For now, we'll just sort by a confidence score (using relevance as a proxy)
    sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
    
    # Prioritize by authority (in a real system, we would use jurisdiction hierarchy)
    # This is just a placeholder based on document title
    def authority_score(chunk):
        title = chunk["document_title"].lower()
        if "supreme court" in title:
            return 3
        elif "statute" in title or "regulation" in title:
            return 2
        else:
            return 1
    
    return sorted(sorted_chunks, key=authority_score, reverse=True)

def prioritize_by_authority(chunks: List[Dict]) -> List[Dict]:
    """
    Prioritize chunks based on authority hierarchy.
    
    For legal documents, we want to prioritize:
    1. Higher court decisions over lower court
    2. More recent decisions over older ones
    3. Statutes and regulations over case law
    
    Args:
        chunks: List of document chunks
        
    Returns:
        Prioritized list of chunks
    """
    # This is a placeholder implementation
    # In a real system, we would implement more sophisticated prioritization
    
    # Simple prioritization based on document title
    def priority_score(chunk):
        title = chunk["document_title"].lower()
        
        # Base score is relevance
        score = chunk["score"] * 10
        
        # Adjust based on document type
        if "supreme court" in title:
            score += 5
        elif "statute" in title:
            score += 4
        elif "regulation" in title:
            score += 3
        elif "court" in title:
            score += 2
        
        return score
    
    return sorted(chunks, key=priority_score, reverse=True)
