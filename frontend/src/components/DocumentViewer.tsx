// Updated implementation of the DocumentViewer component with fixed download
import React, { useState, useEffect } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Grid,
  Chip,
  Divider,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import DescriptionIcon from "@mui/icons-material/Description";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import { DocumentMetadata } from "../types";
import {
  getDocument,
  getDocumentPreview,
  getDocumentDownloadUrl,
  downloadDocument,
} from "../services/api";

interface DocumentViewerProps {
  open: boolean;
  documentId: string | null;
  onClose: () => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  open,
  documentId,
  onClose,
}) => {
  const [document, setDocument] = useState<DocumentMetadata | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<boolean>(false);

  useEffect(() => {
    const fetchDocument = async () => {
      if (!documentId) return;

      setLoading(true);
      setError(null);

      try {
        // Use the API service function to get document metadata
        const documentData = await getDocument(documentId);
        setDocument(documentData);

        // After getting document metadata, fetch the preview
        setPreviewLoading(true);
        try {
          // Use the API service function to get document preview
          const previewData = await getDocumentPreview(documentId);
          setPreview(previewData.preview);
        } catch (previewErr) {
          console.error("Error fetching document preview:", previewErr);
          setPreview("Preview not available for this document type.");
        } finally {
          setPreviewLoading(false);
        }
      } catch (err) {
        console.error("Error fetching document:", err);
        setError("Failed to load document information.");
      } finally {
        setLoading(false);
      }
    };

    if (open && documentId) {
      fetchDocument();
    } else {
      // Reset state when dialog is closed
      setDocument(null);
      setPreview("");
      setError(null);
    }
  }, [open, documentId]);

  const handleDownload = async () => {
    if (!documentId || !document) return;

    try {
      setDownloading(true);

      // Use our improved direct download function
      await downloadDocument(
        documentId,
        document.title || document.filename || "document"
      );
    } catch (error) {
      console.error("Error downloading document:", error);
      setError("Failed to download document. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Not specified";

    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch (e) {
      return dateString;
    }
  };

  if (!open) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: "80vh", display: "flex", flexDirection: "column" },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        {loading
          ? "Loading Document..."
          : document
          ? document.title
          : "Document Viewer"}
      </DialogTitle>

      <DialogContent
        sx={{ display: "flex", flexDirection: "column", flexGrow: 1, py: 1 }}
      >
        {loading ? (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
            }}
          >
            <CircularProgress />
          </Box>
        ) : error ? (
          <Box sx={{ p: 2, color: "error.main" }}>
            <Typography>{error}</Typography>
          </Box>
        ) : document ? (
          <>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <DescriptionIcon sx={{ mr: 1, color: "primary.main" }} />
                  <Typography variant="body1">
                    <strong>Type:</strong>{" "}
                    {document.document_type || "Not specified"}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <CalendarTodayIcon sx={{ mr: 1, color: "primary.main" }} />
                  <Typography variant="body1">
                    <strong>Date:</strong> {formatDate(document.date)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <LocationOnIcon sx={{ mr: 1, color: "primary.main" }} />
                  <Typography variant="body1">
                    <strong>Jurisdiction:</strong>{" "}
                    {document.jurisdiction || "Not specified"}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <DescriptionIcon sx={{ mr: 1, color: "primary.main" }} />
                  <Typography variant="body1">
                    <strong>Size:</strong> {(document.size / 1024).toFixed(2)}{" "}
                    KB
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 1 }} />

            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h6">Document Preview</Typography>
              <Chip
                label={document.status}
                color={
                  document.status === "processed"
                    ? "success"
                    : document.status === "processing"
                    ? "warning"
                    : "error"
                }
                size="small"
              />
            </Box>

            <Paper
              variant="outlined"
              sx={{
                p: 2,
                flexGrow: 1,
                overflow: "auto",
                backgroundColor: "#f9f9f9",
                fontFamily: "monospace",
                fontSize: "0.875rem",
                whiteSpace: "pre-wrap",
              }}
            >
              {previewLoading ? (
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    height: "100%",
                  }}
                >
                  <CircularProgress size={24} />
                </Box>
              ) : preview ? (
                preview
              ) : (
                <Typography color="text.secondary">
                  No preview available for this document type.
                </Typography>
              )}
            </Paper>
          </>
        ) : (
          <Typography>No document selected.</Typography>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        {document && (
          <Button
            variant="contained"
            startIcon={
              downloading ? <CircularProgress size={20} /> : <DownloadIcon />
            }
            onClick={handleDownload}
            disabled={downloading}
            sx={{ mr: "auto" }}
          >
            {downloading ? "Downloading..." : "Download Document"}
          </Button>
        )}
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentViewer;
