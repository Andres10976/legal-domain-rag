"""
Tests for the semantic search module.
"""
import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np

from search.semantic_search import (
    generate_embedding,
    cosine_similarity,
    keyword_match_score,
    hybrid_search,
    apply_filters,
    retrieve_relevant_chunks,
)

@pytest.fixture
def sample_chunks():
    """Sample document chunks for testing."""
    return [
        {
            "chunk_id": "doc1_chunk1",
            "document_id": "doc1",
            "document_title": "Test Document 1",
            "text": "This is a sample legal document about contracts.",
            "embedding": [0.1, 0.2, 0.3, 0.4],
            "metadata": {
                "document_type": "contract",
                "jurisdiction": "California"
            }
        },
        {
            "chunk_id": "doc1_chunk2",
            "document_id": "doc1",
            "document_title": "Test Document 1",
            "text": "The party of the first part shall be known as the party of the first part.",
            "embedding": [0.2, 0.3, 0.4, 0.5],
            "metadata": {
                "document_type": "contract",
                "jurisdiction": "California"
            }
        },
        {
            "chunk_id": "doc2_chunk1",
            "document_id": "doc2",
            "document_title": "Test Document 2",
            "text": "This case establishes precedent for future litigation.",
            "embedding": [0.3, 0.4, 0.5, 0.6],
            "metadata": {
                "document_type": "case_law",
                "jurisdiction": "Federal"
            }
        }
    ]

def test_generate_embedding():
    """Test generating embeddings from text."""
    embedding = generate_embedding("Test query")
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)

def test_cosine_similarity():
    """Test cosine similarity calculation."""
    vec1 = [1, 0, 0, 0]
    vec2 = [0, 1, 0, 0]
    vec3 = [1, 1, 0, 0]
    
    # Orthogonal vectors should have similarity 0
    assert cosine_similarity(vec1, vec2) == 0
    
    # Same vector should have similarity 1
    assert cosine_similarity(vec1, vec1) == 1
    
    # Similar vectors should have similarity between 0 and 1
    assert 0 < cosine_similarity(vec1, vec3) < 1
    
    # Test with zero vector
    assert cosine_similarity(vec1, [0, 0, 0, 0]) == 0

def test_keyword_match_score():
    """Test keyword matching score calculation."""
    text = "This is a sample legal document about contracts and laws."
    
    # Exact match
    assert keyword_match_score("contracts", text) == 1.0
    
    # No match
    assert keyword_match_score("patent", text) == 0.0
    
    # Partial match
    assert keyword_match_score("legal contracts", text) == 0.5
    
    # Empty query
    assert keyword_match_score("", text) == 0.0

def test_hybrid_search(sample_chunks):
    """Test hybrid search functionality."""
    with patch('search.semantic_search.generate_embedding') as mock_embedding:
        mock_embedding.return_value = [0.2, 0.3, 0.4, 0.5]
        
        # Basic search
        results = hybrid_search("contract", sample_chunks, top_k=2, threshold=0.5)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        assert all("score" in result for result in results)
        assert all(result["score"] >= 0.5 for result in results)
        
        # Results should be sorted by score (descending)
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i+1]["score"]

def test_apply_filters(sample_chunks):
    """Test applying filters to document chunks."""
    # Filter by document type
    contract_chunks = apply_filters(sample_chunks, {"document_type": "contract"})
    assert len(contract_chunks) == 2
    assert all(chunk["metadata"]["document_type"] == "contract" for chunk in contract_chunks)
    
    # Filter by jurisdiction
    ca_chunks = apply_filters(sample_chunks, {"jurisdiction": "California"})
    assert len(ca_chunks) == 2
    assert all(chunk["metadata"]["jurisdiction"] == "California" for chunk in ca_chunks)
    
    # Filter by multiple criteria
    filtered_chunks = apply_filters(sample_chunks, {
        "document_type": "contract",
        "jurisdiction": "California"
    })
    assert len(filtered_chunks) == 2
    
    # Filter with no matches
    no_matches = apply_filters(sample_chunks, {"jurisdiction": "New York"})
    assert len(no_matches) == 0
    
    # No filters should return all chunks
    all_chunks = apply_filters(sample_chunks, {})
    assert len(all_chunks) == len(sample_chunks)

@patch('os.path.exists')
@patch('builtins.open')
@patch('json.load')
@patch('search.semantic_search.hybrid_search')
def test_retrieve_relevant_chunks(
    mock_hybrid_search,
    mock_json_load,
    mock_open,
    mock_path_exists,
    sample_chunks
):
    """Test retrieving relevant chunks from the vector database."""
    # Mock the file operations
    mock_path_exists.return_value = True
    mock_json_load.return_value = sample_chunks
    mock_hybrid_search.return_value = [
        {
            "chunk_id": "doc1_chunk1",
            "document_id": "doc1",
            "document_title": "Test Document 1",
            "text": "This is a sample legal document about contracts.",
            "score": 0.8
        }
    ]
    
    # Test basic retrieval
    results = retrieve_relevant_chunks("contract")
    
    assert isinstance(results, list)
    assert len(results) > 0
    mock_hybrid_search.assert_called_once()
    
    # Test with filters
    retrieve_relevant_chunks("contract", {"document_type": "contract"})
    
    # Test with custom parameters
    retrieve_relevant_chunks("contract", top_k=10, threshold=0.3)
    
    # Test when vector DB doesn't exist
    mock_path_exists.return_value = False
    empty_results = retrieve_relevant_chunks("contract")
    assert len(empty_results) == 0
