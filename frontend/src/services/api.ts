import axios from 'axios';
import {
  DocumentList,
  DocumentMetadata,
  DocumentResponse,
  QueryRequest,
  QueryResponse,
  ConversationHistory,
  SystemStats,
  SystemConfig,
  SystemConfigUpdate,
} from '../types';

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document API
export const uploadDocument = async (formData: FormData): Promise<DocumentResponse> => {
  const response = await api.post<DocumentResponse>('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (): Promise<DocumentList> => {
  const response = await api.get<DocumentList>('/documents');
  return response.data;
};

export const getDocument = async (id: string): Promise<DocumentMetadata> => {
  const response = await api.get<DocumentMetadata>(`/documents/${id}`);
  return response.data;
};

export const deleteDocument = async (id: string): Promise<DocumentResponse> => {
  const response = await api.delete<DocumentResponse>(`/documents/${id}`);
  return response.data;
};

// Query API
export const queryDocuments = async (queryRequest: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>('/query', queryRequest);
  return response.data;
};

export const getHistory = async (): Promise<ConversationHistory> => {
  const response = await api.get<ConversationHistory>('/history');
  return response.data;
};

// Admin API
export const getSystemStats = async (): Promise<SystemStats> => {
  const response = await api.get<SystemStats>('/admin/stats');
  return response.data;
};

export const getSystemConfig = async (): Promise<SystemConfig> => {
  const response = await api.get<SystemConfig>('/admin/config');
  return response.data;
};

export const updateSystemConfig = async (config: SystemConfigUpdate): Promise<SystemConfig> => {
  const response = await api.post<SystemConfig>('/admin/config', config);
  return response.data;
};

export const reindexDocuments = async (): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>('/admin/reindex');
  return response.data;
};

export default api;
