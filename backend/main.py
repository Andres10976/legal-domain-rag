"""
Main entry point for the Legal Domain RAG System backend.
"""
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Import routes
from api.routes import documents, queries, admin

# Create FastAPI app
app = FastAPI(
    title="Legal Domain RAG System",
    description="A specialized Retrieval-Augmented Generation system for legal documents",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(queries.router, prefix="/api", tags=["queries"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files for document access
app.mount("/documents", StaticFiles(directory="uploads"), name="documents")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
