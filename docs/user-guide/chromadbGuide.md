# ChromaDB Integration

This document explains how the Legal Domain RAG System integrates with ChromaDB to provide vector search capabilities.

## What is ChromaDB?

ChromaDB is an open-source embedding database designed to store and search vector embeddings. It is:

- **Local**: Runs entirely on your machine with no external API calls
- **Fast**: Optimized for quick similarity searches
- **Simple**: Easy to use and integrate with Python applications
- **Free**: Open-source with no usage costs

## How We Use ChromaDB

In our system, ChromaDB serves as the vector database that stores document chunks and their embeddings. Key features we utilize:

1. **Persistent Storage**: Document embeddings are stored on disk for retrieval across sessions
2. **Similarity Search**: Finding the most relevant document chunks for a query
3. **Metadata Filtering**: Filtering results based on document metadata (type, jurisdiction, etc.)
4. **Document Management**: Adding, updating, and deleting document chunks

## Implementation Details

### Collection Structure

We use a single ChromaDB collection named `legal_documents` with the following structure:

- **IDs**: Unique chunk identifiers in the format `{document_id}_chunk_{n}`
- **Embeddings**: Vector representations of text chunks (384 dimensions for MiniLM-L6-v2)
- **Documents**: The actual text content of each chunk
- **Metadatas**: Document metadata including:
  - `document_id`: The parent document identifier
  - `document_title`: The document title
  - `document_type`: The type of document (contract, case law, etc.)
  - `jurisdiction`: The legal jurisdiction (if applicable)
  - `date`: The document date (if available)

### Initialization

The ChromaDB collection is initialized at startup:

```python
def initialize_collection():
    """
    Initialize or get the ChromaDB collection for document storage.
    """
    try:
        collection = client.get_collection(name="legal_documents", embedding_function=default_ef)
        print(f"Retrieved existing collection 'legal_documents'")
    except Exception:
        collection = client.create_collection(name="legal_documents", embedding_function=default_ef)
        print(f"Created new collection 'legal_documents'")

    return collection
```

### Adding Documents

When documents are processed, their chunks are added to ChromaDB:

```python
def add_documents(chunks: List[Dict]):
    """
    Add document chunks to the vector database.
    """
    collection = initialize_collection()

    # Format data for ChromaDB
    ids = [chunk["chunk_id"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = []

    for chunk in chunks:
        # Extract and format metadata for ChromaDB
        metadata = {...}
        metadatas.append(metadata)

    # Add data to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
```

### Querying Documents

When a user submits a query, we convert it to an embedding and search ChromaDB:

```python
def query_documents(
    query_text: str,
    filters: Optional[Dict] = None,
    top_k: int = 5,
    threshold: float = 0.3
) -> List[Dict]:
    """
    Query the vector database for relevant document chunks.
    """
    collection = initialize_collection()

    # Format filters for ChromaDB if provided
    where_clause = {}
    if filters:
        for key, value in filters.items():
            where_clause[key] = value

    # Query the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k * 2,  # Get more results than needed for post-filtering
        where=where_clause if where_clause else None
    )

    # Format and filter results
    chunks = []
    for i in range(len(results["ids"][0])):
        # Calculate normalized similarity score
        distance = results["distances"][0][i] if "distances" in results else 0.5
        similarity_score = 1.0 - (distance / 2.0)  # Normalize to 0-1 range

        # Only include results above threshold
        if similarity_score >= threshold:
            chunks.append({
                "chunk_id": results["ids"][0][i],
                "document_id": results["metadatas"][0][i]["document_id"],
                "document_title": results["metadatas"][0][i]["document_title"],
                "text": results["documents"][0][i],
                "score": similarity_score
            })

    # Sort by score and limit to top_k
    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]
```

## Configuration

The ChromaDB integration is configured through environment variables:

```
# ChromaDB Configuration
CHROMA_PERSIST_DIR=vector_db/chroma
```

## Performance Considerations

- **Embedding Dimension**: We use 384-dimensional embeddings (MiniLM-L6-v2) for a good balance of accuracy and performance
- **Collection Size**: ChromaDB performs well with collections of up to 1 million chunks on standard hardware
- **Query Time**: Typical query time is under 100ms for collections with thousands of documents
- **Disk Usage**: Expect approximately 1.5KB of storage per chunk (including the embedding, text, and metadata)

## Future Enhancements

Potential improvements to our ChromaDB integration:

1. **Multiple Collections**: Separating documents by type or jurisdiction into different collections
2. **Parallel Processing**: Batch processing for faster document ingestion
3. **Optimized Retrieval**: Experimenting with hybrid retrieval methods (embedding + keyword)
4. **Advanced Filtering**: More sophisticated metadata filtering options
