// Document Types
export interface DocumentMetadata {
  id: string;
  filename: string;
  title: string | null;
  document_type: string | null;
  jurisdiction: string | null;
  date: string | null;
  uploaded_at: string;
  status: string;
  size: number;
}

export interface DocumentList {
  documents: DocumentMetadata[];
}

export interface DocumentResponse {
  id: string;
  message: string;
}

// Query Types
export interface QueryRequest {
  query: string;
  filters?: Record<string, any> | null;
  chunk_count?: number;
  similarity_threshold?: number;
}

export interface Citation {
  document_id: string;
  document_title: string;
  chunk_id: string;
  text: string;
  relevance_score: number;
}

export interface QueryResponse {
  query: string;
  response: string;
  citations: Citation[];
  confidence_score: number;
}

export interface HistoryItem {
  query: string;
  response: string;
  timestamp: string;
}

export interface ConversationHistory {
  history: HistoryItem[];
}

// Admin Types
export interface SystemStats {
  document_count: number;
  total_chunks: number;
  vector_store_size: string;
  avg_query_time: number;
}

export interface SystemConfig {
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  similarity_threshold: number;
}

export interface SystemConfigUpdate {
  embedding_model?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  similarity_threshold?: number;
}
