"""
Document processing module.

Handles the extraction of text from various document formats,
chunking strategies, and embedding generation.
"""
import os
import json
import tempfile
from typing import Dict, List, Any
import pypdf
import docx2txt
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import ChromaDB store
from search.chroma_store import add_documents

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

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Sentence Transformers.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    # Generate embeddings
    embeddings = embedding_model.encode(texts)
    
    # Convert to list of lists
    return embeddings.tolist()

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text
    """
    text = ""
    try:
        pdf = pypdf.PdfReader(file_path)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text
    """
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        Extracted text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try another encoding if utf-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT file: {str(e)}")
            return ""
    except Exception as e:
        print(f"Error reading TXT file: {str(e)}")
        return ""

def extract_text(file_path: str) -> str:
    """
    Extract text from a document based on its extension.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Extracted text
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def chunk_text(text: str, metadata: Dict) -> List[Dict]:
    """
    Split text into chunks with adaptive strategies.
    
    For legal documents, we want to preserve structure like sections,
    paragraphs, and lists.
    
    Args:
        text: Document text
        metadata: Document metadata
        
    Returns:
        List of document chunks
    """
    # Get chunk size and overlap from environment variables or use defaults
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    
    # Split text into chunks
    chunks = text_splitter.split_text(text)
    
    # Create document chunks with metadata
    doc_chunks = []
    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{metadata['id']}_chunk_{i}"
        doc_chunks.append({
            "chunk_id": chunk_id,
            "document_id": metadata["id"],
            "document_title": metadata["title"],
            "text": chunk_text,
            "metadata": metadata,
            "embedding": None  # Will be populated later
        })
    
    return doc_chunks

def save_chunks_to_json(chunks: List[Dict], doc_id: str):
    """
    Save chunks to a JSON file for later reference.
    
    Args:
        chunks: List of document chunks
        doc_id: Document ID
    """
    os.makedirs("processed", exist_ok=True)
    with open(f"processed/{doc_id}_chunks.json", "w") as f:
        # Create a copy of chunks with simplified embedding data for readability
        chunks_copy = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            # Replace embedding with dimension info to keep file size reasonable
            if chunk_copy["embedding"] is not None:
                chunk_copy["embedding"] = f"<{len(chunk_copy['embedding'])} dimensions>"
            chunks_copy.append(chunk_copy)
        
        json.dump(chunks_copy, f, indent=2)

def update_metadata_status(metadata: Dict, status: str):
    """
    Update metadata status.
    
    Args:
        metadata: Document metadata
        status: New status
    """
    metadata["status"] = status
    # Save metadata to file
    os.makedirs("metadata", exist_ok=True)
    with open(f"metadata/{metadata['id']}.json", "w") as f:
        json.dump(metadata, f, indent=2)

def process_document(file_path: str, metadata: Dict):
    """
    Process a document: extract text, chunk it, generate embeddings, and store in vector DB.
    
    Args:
        file_path: Path to the document file
        metadata: Document metadata
    """
    try:
        print(f"Processing document: {metadata['filename']}")
        
        # Extract text from document
        text = extract_text(file_path)
        
        if not text:
            print(f"No text extracted from document: {metadata['filename']}")
            update_metadata_status(metadata, "error")
            return
        
        print(f"Extracted {len(text)} characters from document")
        
        # Chunk text
        chunks = chunk_text(text, metadata)
        
        print(f"Split document into {len(chunks)} chunks")
        
        # Generate embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)
        
        # Add embeddings to chunks
        for i, embedding in enumerate(embeddings):
            chunks[i]["embedding"] = embedding
        
        # Save chunks to JSON for reference
        save_chunks_to_json(chunks, metadata["id"])
        
        # Store in ChromaDB
        add_documents(chunks)
        
        # Update metadata status
        update_metadata_status(metadata, "processed")
        
        print(f"Document processing complete: {metadata['filename']}")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        update_metadata_status(metadata, "error")
