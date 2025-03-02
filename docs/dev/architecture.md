# System Architecture

The Legal Domain RAG System follows a modular architecture designed for scalability, maintainability, and performance.

## High-Level Architecture

```
[Document Sources] → [Ingestion Pipeline] → [Vector Database]
                                            ↑
[Web UI] → [API Gateway] → [Query Processor] → [LLM Service]
```

## Component Overview

### Frontend Components

- **Web UI**: React-based single-page application
  - Document upload and management interface
  - Query interface with response display
  - Administration interface

### Backend Components

- **API Gateway**: FastAPI application that handles all requests
  - Document upload and management
  - Query processing
  - Administrative functions

- **Document Ingestion Pipeline**:
  - Text extraction from various file formats (PDF, DOCX, TXT)
  - Document metadata extraction
  - Text chunking with legal-domain awareness
  - Embedding generation

- **Vector Database**:
  - Storage for document chunks and embeddings
  - Efficient similarity search
  - Integration with various vector DB providers (Chroma, Pinecone, Weaviate)

- **Semantic Search Module**:
  - Query embedding generation
  - Hybrid retrieval (combining semantic and keyword search)
  - Metadata filtering

- **Context Assembly Module**:
  - Assembly of retrieved chunks into coherent context
  - Context window management
  - Source attribution tracking
  - Contradiction detection and resolution

- **Response Generation Module**:
  - Integration with LLM providers (Claude, OpenAI, Gemini)
  - Legal-domain prompt engineering
  - Response verification
  - Citation formatting

## Data Flow

1. **Document Ingestion**:
   - User uploads document through Web UI
   - API Gateway receives the document and metadata
   - Document Processor extracts text
   - Text is chunked and embeddings are generated
   - Chunks and embeddings are stored in Vector Database

2. **Query Processing**:
   - User submits query through Web UI
   - API Gateway receives the query
   - Query Processor converts query to embedding
   - Vector Database returns relevant chunks
   - Context Assembly creates coherent prompt
   - LLM Service generates response
   - Response with citations returned to user

## Technology Stack

- **Frontend**:
  - React.js with TypeScript
  - Material-UI component library
  - Axios for API communication

- **Backend**:
  - Python 3.9+
  - FastAPI web framework
  - LangChain for RAG components
  - Sentence Transformers for embeddings

- **Databases**:
  - Vector database (Chroma/Pinecone/Weaviate)
  - File system for document storage

- **External Services**:
  - LLM API (Claude/OpenAI/Gemini)

## Deployment Architecture

The system is containerized using Docker, allowing for flexible deployment options:

- **Development**: Local deployment with Docker Compose
- **Testing**: CI/CD pipeline with automated testing
- **Production**: Container deployment on lightweight cloud services

For larger scale deployments, the architecture can be adapted to use:
- Separate database servers
- Load balancing for API servers
- CDN for static frontend assets
