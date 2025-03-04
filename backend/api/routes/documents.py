"""
API routes for document management (upload, listing, deletion).
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import json

# Import services
from ingestion.document_processor import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

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

@router.post("/upload", response_model=DocumentResponse)
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
    
    # Save metadata
    os.makedirs("metadata", exist_ok=True)
    with open(f"metadata/{doc_id}.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Process document in background
    background_tasks.add_task(process_document, file_path, metadata)
    
    return {"id": doc_id, "message": "Document uploaded and queued for processing"}

@router.get("", response_model=DocumentList)
async def list_documents():
    """
    List all uploaded documents with their metadata and processing status.
    """
    documents = []
    if os.path.exists("uploads"):
        for filename in os.listdir("uploads"):
            file_path = os.path.join("uploads", filename)
            if os.path.isfile(file_path):
                # Get document ID (UUID) from filename
                doc_id = os.path.splitext(filename)[0]
                
                # Default metadata in case we can't find the metadata file
                doc_metadata = {
                    "id": doc_id,
                    "filename": filename,
                    "title": filename,
                    "document_type": "unknown",
                    "jurisdiction": "unknown",
                    "date": "",
                    "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    "status": "processed",
                    "size": os.path.getsize(file_path)
                }
                
                # Try to load metadata from metadata file
                metadata_path = f"metadata/{doc_id}.json"
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            stored_metadata = json.load(f)
                            
                            # Update document metadata with stored values
                            doc_metadata.update(stored_metadata)
                    except Exception as e:
                        print(f"Error loading metadata for {doc_id}: {str(e)}")
                
                documents.append(doc_metadata)
    
    return {"documents": documents}

@router.get("/{doc_id}", response_model=DocumentMetadata)
async def get_document(doc_id: str):
    """
    Get metadata for a specific document.
    """
    # First, check if metadata file exists
    metadata_path = f"metadata/{doc_id}.json"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                
                # Ensure all required fields are present
                if "id" not in metadata:
                    metadata["id"] = doc_id
                
                # Get file path to check if file still exists
                for ext in [".pdf", ".docx", ".txt"]:
                    file_path = f"uploads/{doc_id}{ext}"
                    if os.path.exists(file_path):
                        # Update file size in case it changed
                        metadata["size"] = os.path.getsize(file_path)
                        return metadata
                        
                # If we get here, the file doesn't exist anymore
                raise HTTPException(status_code=404, detail="Document file not found")
                
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error reading document metadata")
    
    # If metadata file doesn't exist, check if document file exists
    for ext in [".pdf", ".docx", ".txt"]:
        file_path = f"uploads/{doc_id}{ext}"
        if os.path.exists(file_path):
            # Create basic metadata
            return {
                "id": doc_id,
                "filename": os.path.basename(file_path),
                "title": os.path.basename(file_path),
                "document_type": ext[1:].upper(),  # Use extension as type (.pdf -> PDF)
                "jurisdiction": "Unknown",
                "date": "",
                "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "status": "processed",
                "size": os.path.getsize(file_path)
            }
    
    # If we get here, neither metadata nor document file exists
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/{doc_id}/content")
async def get_document_content(doc_id: str, preview: bool = False):
    """
    Get the content of a document.
    
    If preview=True, returns a JSON with document preview text.
    Otherwise, returns the document file directly for download.
    """
    # Find the document file
    document_path = None
    for ext in [".pdf", ".docx", ".txt"]:
        file_path = f"uploads/{doc_id}{ext}"
        if os.path.exists(file_path):
            document_path = file_path
            break
    
    if not document_path:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if preview:
        # Generate preview text
        try:
            from ingestion.document_processor import extract_text
            
            # Get the first 2000 characters as preview
            text = extract_text(document_path)
            preview_text = text[:2000]
            if len(text) > 2000:
                preview_text += "...\n\n[Content truncated. Download the full document to see more.]"
            
            return JSONResponse({
                "preview": preview_text,
                "extension": os.path.splitext(document_path)[1][1:],
                "size": os.path.getsize(document_path)
            })
        except Exception as e:
            print(f"Error generating document preview: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating document preview: {str(e)}")
    else:
        # Return the document file for download
        original_filename = os.path.basename(document_path)
        
        # Add the original filename to the Content-Disposition header
        return FileResponse(
            path=document_path, 
            filename=original_filename,  # Use original filename in Content-Disposition 
            media_type="application/octet-stream"
        )

@router.delete("/{doc_id}", response_model=DocumentResponse)
async def delete_document(doc_id: str):
    """
    Delete a document and its associated data.
    """
    deleted = False
    
    # Delete document file
    for ext in [".pdf", ".docx", ".txt"]:
        file_path = f"uploads/{doc_id}{ext}"
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted = True
    
    # Delete metadata file
    metadata_path = f"metadata/{doc_id}.json"
    if os.path.exists(metadata_path):
        os.remove(metadata_path)
        deleted = True
    
    # Delete processed chunks
    processed_path = f"processed/{doc_id}_chunks.json"
    if os.path.exists(processed_path):
        os.remove(processed_path)
        deleted = True
    
    # Delete from vector store
    try:
        # Import the delete_document function from the chroma_store module
        from search.chroma_store import delete_document as delete_from_vector_db
        
        # Call the function to delete the document chunks from the vector database
        success = delete_from_vector_db(doc_id)
        
        if success:
            print(f"Successfully deleted document {doc_id} from vector database")
        else:
            print(f"No entries found for document {doc_id} in vector database")
            
    except Exception as e:
        print(f"Error deleting document from vector database: {str(e)}")
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"id": doc_id, "message": "Document deleted successfully"}