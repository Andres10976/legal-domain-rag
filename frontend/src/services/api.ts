import axios from "axios";
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
} from "../types";

// Create axios instance
const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Document API
export const uploadDocument = async (
  formData: FormData
): Promise<DocumentResponse> => {
  const response = await api.post<DocumentResponse>(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};

export const getDocuments = async (): Promise<DocumentList> => {
  const response = await api.get<DocumentList>("/documents");
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
export const queryDocuments = async (
  queryRequest: QueryRequest
): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>("/query", queryRequest);
  return response.data;
};

export const getHistory = async (): Promise<ConversationHistory> => {
  const response = await api.get<ConversationHistory>("/history");
  return response.data;
};

// Admin API
export const getSystemStats = async (): Promise<SystemStats> => {
  const response = await api.get<SystemStats>("/admin/stats");
  return response.data;
};

export const getSystemConfig = async (): Promise<SystemConfig> => {
  const response = await api.get<SystemConfig>("/admin/config");
  return response.data;
};

export const updateSystemConfig = async (
  config: SystemConfigUpdate
): Promise<SystemConfig> => {
  const response = await api.post<SystemConfig>("/admin/config", config);
  return response.data;
};

export const reindexDocuments = async (): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>("/admin/reindex");
  return response.data;
};

export const getDocumentPreview = async (
  id: string
): Promise<{ preview: string; extension: string; size: number }> => {
  const response = await api.get<{
    preview: string;
    extension: string;
    size: number;
  }>(`/documents/${id}/content?preview=true`);
  return response.data;
};

export const getDocumentDownloadUrl = (id: string): string => {
  return `/api/documents/${id}/content`;
};

export const downloadDocument = async (
  id: string,
  filename: string
): Promise<void> => {
  try {
    // Make a direct fetch request to get the file with proper headers
    const response = await fetch(`/api/documents/${id}/content`, {
      method: "GET",
      headers: {
        Accept: "application/octet-stream",
      },
    });

    if (!response.ok) {
      throw new Error(`Error downloading file: ${response.statusText}`);
    }

    // Get the blob from the response
    const blob = await response.blob();

    // Create a URL for the blob
    const url = window.URL.createObjectURL(blob);

    // Create a temporary link element
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;

    // Append to the document, click it, and remove it
    document.body.appendChild(link);
    link.click();

    // Clean up
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);
  } catch (error) {
    console.error("Error downloading document:", error);
    throw error;
  }
};

export default api;
