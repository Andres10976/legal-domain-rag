"""
Tests for the document processing module.
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from ingestion.document_processor import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_text,
    chunk_text,
    save_chunks_to_json,
    process_document,
)

@pytest.fixture
def sample_metadata():
    """Sample document metadata for testing."""
    return {
        "id": "test-doc-123",
        "filename": "test_document.pdf",
        "title": "Test Document",
        "document_type": "Test",
        "jurisdiction": "Test",
        "date": "2023-01-01",
        "uploaded_at": "2023-01-01T12:00:00",
        "status": "processing",
        "size": 1024
    }

@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample legal document for testing.
    
    Section 1: Introduction
    This document is created solely for testing purposes.
    
    Section 2: Legal Content
    The party of the first part shall be known in this agreement as the party of the first part.
    The party of the second part shall be known in this agreement as the party of the second part.
    
    Section 3: Conclusion
    In witness whereof, the parties have executed this agreement as of the date first written above.
    """

def test_extract_text_from_txt():
    """Test extracting text from a TXT file."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
        content = "This is a test document."
        temp.write(content.encode('utf-8'))
        temp.flush()
        
        result = extract_text_from_txt(temp.name)
        
    os.unlink(temp.name)
    assert result == content

@patch('pypdf.PdfReader')
def test_extract_text_from_pdf(mock_pdf_reader):
    """Test extracting text from a PDF file."""
    # Mock PDF reader
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is a test page."
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page, mock_page]
    mock_pdf_reader.return_value = mock_pdf
    
    result = extract_text_from_pdf("dummy.pdf")
    
    assert result == "This is a test page.\nThis is a test page.\n"
    mock_pdf_reader.assert_called_once_with("dummy.pdf")

@patch('docx2txt.process')
def test_extract_text_from_docx(mock_process):
    """Test extracting text from a DOCX file."""
    mock_process.return_value = "This is a test document."
    
    result = extract_text_from_docx("dummy.docx")
    
    assert result == "This is a test document."
    mock_process.assert_called_once_with("dummy.docx")

def test_extract_text():
    """Test the extract_text function with different file types."""
    with patch('ingestion.document_processor.extract_text_from_pdf') as mock_pdf, \
         patch('ingestion.document_processor.extract_text_from_docx') as mock_docx, \
         patch('ingestion.document_processor.extract_text_from_txt') as mock_txt:
        
        mock_pdf.return_value = "PDF content"
        mock_docx.return_value = "DOCX content"
        mock_txt.return_value = "TXT content"
        
        assert extract_text("test.pdf") == "PDF content"
        assert extract_text("test.docx") == "DOCX content"
        assert extract_text("test.txt") == "TXT content"
        
        with pytest.raises(ValueError):
            extract_text("test.unknown")

def test_chunk_text(sample_text, sample_metadata):
    """Test chunking text into smaller pieces."""
    chunks = chunk_text(sample_text, sample_metadata)
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "document_id" in chunk
        assert "document_title" in chunk
        assert "text" in chunk
        assert "metadata" in chunk
        assert chunk["document_id"] == sample_metadata["id"]
        assert chunk["document_title"] == sample_metadata["title"]

@patch('builtins.open')
@patch('json.dump')
def test_save_chunks_to_json(mock_json_dump, mock_open, sample_metadata):
    """Test saving chunks to a JSON file."""
    chunks = [{"chunk_id": "test_chunk"}]
    
    save_chunks_to_json(chunks, sample_metadata["id"])
    
    mock_open.assert_called_once()
    mock_json_dump.assert_called_once()

@patch('ingestion.document_processor.extract_text')
@patch('ingestion.document_processor.chunk_text')
@patch('ingestion.document_processor.generate_embeddings')
@patch('ingestion.document_processor.save_chunks_to_json')
@patch('ingestion.document_processor.store_in_vector_db')
@patch('ingestion.document_processor.update_metadata_status')
def test_process_document(
    mock_update_status,
    mock_store,
    mock_save,
    mock_embeddings,
    mock_chunk,
    mock_extract,
    sample_metadata
):
    """Test the full document processing pipeline."""
    # Mock the functions
    mock_extract.return_value = "Test document content"
    mock_chunk.return_value = [
        {"chunk_id": "chunk1", "text": "Test chunk 1"},
        {"chunk_id": "chunk2", "text": "Test chunk 2"}
    ]
    mock_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
    
    # Process the document
    process_document("test.pdf", sample_metadata)
    
    # Verify function calls
    mock_extract.assert_called_once_with("test.pdf")
    mock_chunk.assert_called_once()
    mock_embeddings.assert_called_once()
    mock_save.assert_called_once()
    mock_store.assert_called_once()
    mock_update_status.assert_called_once_with(sample_metadata, "processed")
