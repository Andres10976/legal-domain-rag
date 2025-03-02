"""
Shared test fixtures and configuration.
"""
import os
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test")

# Import after environment variables are loaded
from main import app

@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)

@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_text():
    """
    Sample text content for testing.
    """
    return """
    LEGAL AGREEMENT
    
    This is a sample legal agreement for testing purposes.
    
    SECTION 1: DEFINITIONS
    
    "Party" means any individual or entity participating in this agreement.
    "Agreement" means this sample legal document.
    
    SECTION 2: TERMS
    
    The parties hereby agree to the following terms:
    
    2.1 This is a test document only.
    2.2 No legal effect shall arise from this document.
    
    SECTION 3: CONCLUSION
    
    This agreement is signed and executed solely for testing.
    """

@pytest.fixture
def pdf_file(temp_dir, sample_text):
    """
    Create a sample PDF file for testing.
    
    Note: This doesn't actually create a real PDF, just a file with .pdf extension.
    In a real test, you might want to use a library like reportlab to create a real PDF.
    """
    file_path = os.path.join(temp_dir, "sample.pdf")
    with open(file_path, "w") as f:
        f.write(sample_text)
    return file_path

@pytest.fixture
def docx_file(temp_dir, sample_text):
    """
    Create a sample DOCX file for testing.
    
    Note: This doesn't actually create a real DOCX, just a file with .docx extension.
    In a real test, you might want to use a library like python-docx to create a real DOCX.
    """
    file_path = os.path.join(temp_dir, "sample.docx")
    with open(file_path, "w") as f:
        f.write(sample_text)
    return file_path

@pytest.fixture
def txt_file(temp_dir, sample_text):
    """
    Create a sample TXT file for testing.
    """
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write(sample_text)
    return file_path

@pytest.fixture
def sample_chunks():
    """
    Sample document chunks for testing.
    """
    return [
        {
            "chunk_id": "doc1_chunk1",
            "document_id": "doc1",
            "document_title": "Sample Contract",
            "text": "This is the first chunk of the sample contract.",
            "metadata": {
                "document_type": "contract",
                "jurisdiction": "California",
                "date": "2023-01-01"
            },
            "embedding": [0.1, 0.2, 0.3, 0.4]
        },
        {
            "chunk_id": "doc1_chunk2",
            "document_id": "doc1",
            "document_title": "Sample Contract",
            "text": "This is the second chunk of the sample contract.",
            "metadata": {
                "document_type": "contract",
                "jurisdiction": "California",
                "date": "2023-01-01"
            },
            "embedding": [0.2, 0.3, 0.4, 0.5]
        },
        {
            "chunk_id": "doc2_chunk1",
            "document_id": "doc2",
            "document_title": "Sample Statute",
            "text": "This is a chunk from a sample statute.",
            "metadata": {
                "document_type": "statute",
                "jurisdiction": "Federal",
                "date": "2022-05-15"
            },
            "embedding": [0.3, 0.4, 0.5, 0.6]
        }
    ]
