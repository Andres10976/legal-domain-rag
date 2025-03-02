"""
Tests for the API endpoints.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from fastapi.testclient import TestClient

# Import the routes to patch their dependencies
import api.routes.documents
import api.routes.queries
import api.routes.admin

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Documents API Tests
@patch('api.routes.documents.process_document')
def test_upload_document(mock_process, client, txt_file):
    """Test document upload endpoint."""
    # Create a test file
    with open(txt_file, 'rb') as f:
        files = {'file': ('test.txt', f, 'text/plain')}
        data = {
            'title': 'Test Document',
            'document_type': 'Test',
            'jurisdiction': 'Test',
            'date': '2023-01-01'
        }
        response = client.post("/api/documents/upload", files=files, data=data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert 'id' in response_data
    assert response_data['message'] == 'Document uploaded and queued for processing'
    
    # Verify process_document was called
    mock_process.assert_called_once()

def test_upload_invalid_document(client):
    """Test uploading a document with invalid extension."""
    files = {'file': ('test.invalid', b'test content', 'application/octet-stream')}
    response = client.post("/api/documents/upload", files=files)
    
    assert response.status_code == 400
    assert "File type not supported" in response.json()['detail']

@patch('os.path.exists')
@patch('os.listdir')
@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('os.path.getctime')
def test_list_documents(
    mock_getctime,
    mock_getsize,
    mock_isfile,
    mock_listdir,
    mock_exists,
    client
):
    """Test listing documents endpoint."""
    # Mock directory operations
    mock_exists.return_value = True
    mock_listdir.return_value = ['doc1.pdf', 'doc2.txt']
    mock_isfile.return_value = True
    mock_getsize.return_value = 1024
    mock_getctime.return_value = 1672531200  # 2023-01-01
    
    response = client.get("/api/documents")
    
    assert response.status_code == 200
    documents = response.json()['documents']
    assert len(documents) == 2

# Query API Tests
@patch('api.routes.queries.retrieve_relevant_chunks')
@patch('api.routes.queries.assemble_context')
@patch('api.routes.queries.generate_response')
def test_query_documents(
    mock_generate_response,
    mock_assemble_context,
    mock_retrieve_chunks,
    client,
    sample_chunks
):
    """Test querying documents endpoint."""
    # Mock the services
    mock_retrieve_chunks.return_value = sample_chunks
    mock_assemble_context.return_value = {"text": "Assembled context", "sources": []}
    mock_generate_response.return_value = ("This is a response", 0.8)
    
    query_data = {
        "query": "What is in the contract?",
        "filters": {"document_type": "contract"},
        "chunk_count": 3,
        "similarity_threshold": 0.3
    }
    
    response = client.post("/api/query", json=query_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["query"] == query_data["query"]
    assert "response" in response_data
    assert "citations" in response_data
    assert "confidence_score" in response_data

# Admin API Tests
@patch('api.routes.admin.get_system_stats')
def test_get_system_stats(mock_get_stats, client):
    """Test getting system stats endpoint."""
    mock_get_stats.return_value = {
        "document_count": 5,
        "total_chunks": 50,
        "vector_store_size": "10 MB",
        "avg_query_time": 0.5
    }
    
    response = client.get("/api/admin/stats")
    
    assert response.status_code == 200
    stats = response.json()
    assert stats["document_count"] == 5
    assert stats["total_chunks"] == 50
    assert stats["vector_store_size"] == "10 MB"
    assert stats["avg_query_time"] == 0.5

@patch('api.routes.admin.get_system_config')
def test_get_system_config(mock_get_config, client):
    """Test getting system configuration endpoint."""
    mock_get_config.return_value = {
        "llm_provider": "anthropic",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_db_provider": "chroma",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "similarity_threshold": 0.3
    }
    
    response = client.get("/api/admin/config")
    
    assert response.status_code == 200
    config = response.json()
    assert config["llm_provider"] == "anthropic"
    assert config["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert config["vector_db_provider"] == "chroma"
    assert config["chunk_size"] == 1000
    assert config["chunk_overlap"] == 200
    assert config["similarity_threshold"] == 0.3
