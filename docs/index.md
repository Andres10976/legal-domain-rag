# Legal Domain RAG System

Welcome to the documentation for the Legal Domain RAG System - a specialized Retrieval-Augmented Generation system focused on legal documents.

## Overview

The Legal Domain RAG System allows legal professionals to query a corpus of legal documents using natural language and receive accurate, context-aware responses with proper citations to the source material.

### Key Features

- **Document Ingestion**: Upload and process legal documents (contracts, case law, statutes, regulations)
- **Semantic Search**: Find relevant information using advanced semantic search algorithms
- **Context-Aware Retrieval**: Assemble coherent context from various document sources
- **Response Generation**: Generate accurate responses with proper legal citations
- **User-Friendly Interface**: Intuitive web interface designed for legal professionals

## Technology Stack

- **Frontend**: React with TypeScript and Material-UI
- **Backend**: Python FastAPI
- **Vector Database**: ChromaDB for semantic search
- **LLM**: Google Gemini for response generation
- **Embedding**: Sentence Transformers for document and query embedding

## Getting Started

To get started with the Legal Domain RAG System:

1. [Set up your environment](dev/environment.md)
2. [Upload your legal documents](user-guide/document-management.md)
3. [Start querying your documents](user-guide/querying.md)

## System Architecture

```
[Document Sources] → [Ingestion Pipeline] → [ChromaDB Vector Database]
                                            ↑
[Web UI] → [API Gateway] → [Query Processor] → [Google Gemini]
```

The system follows a modular architecture with these main components:

- **Frontend**: React-based web application
- **Backend API**: FastAPI application
- **Document Processing Pipeline**: Extracts, chunks, and embeds documents
- **Vector Database**: ChromaDB for semantic search
- **LLM Integration**: Google Gemini for response generation

## How It Works

1. **Document Processing**:

   - Legal documents (PDF, DOCX, TXT) are uploaded through the UI
   - Text is extracted and split into semantic chunks
   - Each chunk is converted to a vector embedding using Sentence Transformers
   - Chunks and embeddings are stored in ChromaDB

2. **Query Processing**:

   - User asks a question in natural language
   - Question is converted to an embedding
   - ChromaDB finds the most relevant document chunks
   - Relevant chunks are assembled into a context
   - Context is sent to Google Gemini with the question
   - Response is generated with citations to the source material

3. **Results Display**:
   - Response is displayed to the user
   - Citations are linked to the original document chunks
   - User can expand citations to view the source text

## Contributing

Contributions to the Legal Domain RAG System are welcome! See the [Development Guide](dev/environment.md) for information on setting up your development environment.
