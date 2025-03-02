"""
API routes for document management (upload, listing, deletion).
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

# Import services
from ingestion.document_processor import process_document

router = APIRouter()

# Models
class DocumentMetadata(BaseModel):
    id: str
    filename: str
    title: str = None
    document_type: str = None
    jurisdiction: str = None
    date: str = None
    uploaded_at: str
    status: str
    size: int

class DocumentList(BaseModel):
    documents: List[DocumentMetadata]
    
class DocumentResponse(BaseModel):
    id: str
    message: str

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    document_type: str = Form(None),
    jurisdiction: str = Form(None),
    date: str = Form(None)
):
    """
    Upload a legal document for processing and indexing.
    Accepts PDF, DOCX, and TXT formats.
    """
    # Validate file extension
    allowed_extensions = [".pdf", ".docx", ".txt"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Please upload {', '.join(allowed_extensions)}"
        )
    
    # Create a unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save the file
    file_path = f"uploads/{doc_id}{ext}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create metadata
    metadata = {
        "id": doc_id,
        "filename": file.filename,
        "title": title or file.filename,
        "document_type": document_type,
        "jurisdiction": jurisdiction,
        "date": date,
        "uploaded_at": datetime.now().isoformat(),
        "status": "processing",
        "size": os.path.getsize(file_path)
    }
    
    # Process document in background
    background_tasks.add_task(process_document, file_path, metadata)
    
    return {"id": doc_id, "message": "Document uploaded and queued for processing"}

@router.get("/documents", response_model=DocumentList)
async def list_documents():
    """
    List all uploaded documents with their metadata and processing status.
    """
    # This is a placeholder - in a real implementation, this would query a database
    # For now, we'll simulate by reading from a directory
    documents = []
    if os.path.exists("uploads"):
        for filename in os.listdir("uploads"):
            file_path = os.path.join("uploads", filename)
            if os.path.isfile(file_path):
                # In a real app, we'd retrieve this from a database
                doc_id = os.path.splitext(filename)[0]
                documents.append({
                    "id": doc_id,
                    "filename": filename,
                    "title": filename,  # In a real app, this would come from metadata
                    "document_type": "unknown",  # Placeholder
                    "jurisdiction": "unknown",  # Placeholder
                    "date": "",  # Empty string instead of None
                    "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    "status": "processed",  # Placeholder
                    "size": os.path.getsize(file_path)
                })
    
    return {"documents": documents}

@router.get("/documents/{doc_id}", response_model=DocumentMetadata)
async def get_document(doc_id: str):
    """
    Get metadata for a specific document.
    """
    # This is a placeholder - in a real implementation, this would query a database
    for ext in [".pdf", ".docx", ".txt"]:
        file_path = f"uploads/{doc_id}{ext}"
        if os.path.exists(file_path):
            return {
                "id": doc_id,
                "filename": os.path.basename(file_path),
                "title": os.path.basename(file_path),  # In a real app, this would come from metadata
                "document_type": "unknown",  # Placeholder
                "jurisdiction": "unknown",  # Placeholder
                "date": "",  # Empty string instead of None
                "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "status": "processed",  # Placeholder
                "size": os.path.getsize(file_path)
            }
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/documents/{doc_id}", response_model=DocumentResponse)
async def delete_document(doc_id: str):
    """
    Delete a document and its associated data.
    """
    deleted = False
    for ext in [".pdf", ".docx", ".txt"]:
        file_path = f"uploads/{doc_id}{ext}"
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # In a real app, we would also remove the document from the vector store
    # and delete any associated metadata
    
    return {"id": doc_id, "message": "Document deleted successfully"}