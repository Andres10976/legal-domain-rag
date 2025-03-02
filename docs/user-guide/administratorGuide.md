# Administration Guide

This guide explains how to administer the Legal Domain RAG System, including configuration management, system monitoring, and maintenance tasks.

## Accessing the Admin Interface

The admin interface is available at the `/admin` route in the web application. This interface provides access to:

- System statistics
- Configuration settings
- Maintenance tools

## System Statistics

The admin dashboard displays key statistics about the system:

- **Document Count**: The number of documents in the system
- **Total Chunks**: The number of document chunks in the vector database
- **Vector Store Size**: The approximate size of the vector database
- **Average Query Time**: The average time to process a query

These statistics help you monitor system performance and resource usage.

## Configuration Settings

The system has several configuration options that can be adjusted through the admin interface:

### Embedding Model

You can choose between two embedding models:

- **MiniLM-L6-v2 (Fast)**: A smaller, faster model that provides good performance for most use cases
- **MPNet (Balanced)**: A larger model that provides higher accuracy at the cost of slightly slower performance

The embedding model is used to convert documents and queries into vector embeddings for semantic search.

### Chunk Settings

Chunking is the process of splitting documents into smaller pieces for more effective retrieval. You can adjust:

- **Chunk Size**: The target size (in characters) for each document chunk
- **Chunk Overlap**: The number of characters that overlap between adjacent chunks

A larger chunk size provides more context for each chunk but may reduce retrieval precision. Overlap helps maintain context between chunks.

### Similarity Threshold

The similarity threshold controls how similar a document chunk must be to the query to be included in the results. A higher threshold means only very relevant chunks will be returned, while a lower threshold will return more results but may include less relevant material.

## Maintenance Tasks

### Reindexing Documents

The "Reindex All Documents" button triggers a reprocessing of all documents in the system. This is useful after:

- Changing the embedding model
- Adjusting chunk settings
- Experiencing database corruption

Reindexing will:

1. Clear the existing vector database
2. Reprocess all documents with the current settings
3. Store the new chunks and embeddings in the vector database

This process may take some time depending on the number and size of documents.

## Environment Variables

While most settings can be adjusted through the admin interface, some core configuration is managed through environment variables in the `.env` file:

```
# API Keys
GOOGLE_API_KEY=your_google_api_key_here

# Vector Database Configuration
CHROMA_PERSIST_DIR=vector_db/chroma

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Document Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
SIMILARITY_THRESHOLD=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

Changes to this file require a server restart to take effect.

## Best Practices

### Document Processing

- **Document Size**: For optimal performance, keep documents under 100 pages each
- **Document Format**: PDF files work best, followed by DOCX and TXT
- **Metadata**: Provide accurate metadata (title, document type, jurisdiction, date) when uploading

### System Configuration

- **Embedding Model**: For large document collections, use the faster MiniLM-L6-v2 model
- **Chunk Size**: 1000 characters works well for most legal documents
- **Chunk Overlap**: An overlap of 200 characters helps maintain context between chunks
- **Similarity Threshold**: A threshold of 0.7 provides a good balance between precision and recall
