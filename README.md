# Legal Domain RAG System

A specialized Retrieval-Augmented Generation system focused on legal documents, providing accurate, context-aware responses with proper citations.

## Project Overview

This system allows legal professionals to query a corpus of legal documents using natural language and receive accurate, context-aware responses with proper citations to the source material.

### Key Features

- Document ingestion for legal texts (contracts, case law, statutes, regulations)
- Semantic search with legal domain optimization using ChromaDB vector database
- Context-aware retrieval with source attribution
- Response generation with Google Gemini API
- User-friendly web interface designed for legal professionals

## System Architecture

```
[Document Sources] → [Ingestion Pipeline] → [ChromaDB Vector Database]
                                             ↑
[Web UI] → [API Gateway] → [Query Processor] → [Google Gemini LLM]
```

### Components

- **Web Frontend**: React-based SPA with TypeScript and Material-UI
- **API Gateway**: FastAPI application handling requests/responses
- **Ingestion Pipeline**: Python service for document processing with SentenceTransformers
- **Query Processor**: Core logic for retrieval and prompt construction
- **Vector Database**: ChromaDB for vector search
- **LLM Service**: Integration with Google Gemini API

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (optional, for containerized deployment)
- A Google API key for Gemini

### Installation

1. Clone this repository

```bash
git clone https://github.com/yourusername/legal-domain-rag.git
cd legal-domain-rag
```

2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your Google API key and other settings
```

4. Initialize the backend

```bash
python init_setup.py
```

5. Start the backend server

```bash
python main.py
```

6. Set up the frontend (in a separate terminal)

```bash
cd frontend
npm install
npm start
```

### Using Docker Compose (Alternative)

If you prefer to use Docker:

1. Configure environment variables

```bash
cd backend
cp .env.example .env
# Edit .env with your Google API key and other settings
```

2. Start the services

```bash
docker-compose up -d
```

## Usage

1. Access the web interface at http://localhost:3000 (or http://localhost:80 if using Docker)
2. Go to the Documents page to upload legal documents
3. Wait for processing to complete
4. Go to the Query page to ask questions about your documents
5. Review responses with citations to source material

## API Documentation

The API documentation is available at http://localhost:8000/docs when the backend server is running.

## Implementation Details

### Vector Database: ChromaDB

We use ChromaDB, a free and open-source embedding database that can run locally. It offers:

- Persistent storage
- Semantic search capabilities
- Metadata filtering
- Document management

### LLM: Google Gemini

We use Google's Gemini model for response generation. It's:

- Cost-effective
- Fast for real-time responses
- Optimized for RAG applications

### Embedding Model: Sentence Transformers

We use Sentence Transformers models for generating embeddings:

- **all-MiniLM-L6-v2**: Fast model with good performance (384 dimensions)
- **all-mpnet-base-v2**: Higher quality model for more accurate retrieval

## Configuration

Key configuration options in the `.env` file:

- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `EMBEDDING_MODEL`: The embedding model to use (default: all-MiniLM-L6-v2)
- `CHUNK_SIZE`: Size of document chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `SIMILARITY_THRESHOLD`: Minimum similarity for retrieval (default: 0.3)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
