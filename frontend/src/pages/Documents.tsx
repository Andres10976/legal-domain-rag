import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { getDocuments, uploadDocument, deleteDocument } from "../services/api";
import { DocumentMetadata } from "../types";

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState<boolean>(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [documentTitle, setDocumentTitle] = useState<string>("");
  const [documentType, setDocumentType] = useState<string>("");
  const [jurisdiction, setJurisdiction] = useState<string>("");
  const [documentDate, setDocumentDate] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await getDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error("Error loading documents:", error);
      setError("Failed to load documents. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      setSelectedFile(file);
      if (!documentTitle) {
        setDocumentTitle(file.name);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file to upload.");
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append("file", selectedFile);

      if (documentTitle) {
        formData.append("title", documentTitle);
      }

      if (documentType) {
        formData.append("document_type", documentType);
      }

      if (jurisdiction) {
        formData.append("jurisdiction", jurisdiction);
      }

      if (documentDate) {
        formData.append("date", documentDate);
      }

      await uploadDocument(formData);

      // Reset form
      setSelectedFile(null);
      setDocumentTitle("");
      setDocumentType("");
      setJurisdiction("");
      setDocumentDate("");

      // Reload document list
      loadDocuments();
    } catch (error) {
      console.error("Error uploading document:", error);
      setError("Failed to upload document. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteConfirm = (id: string) => {
    setDocumentToDelete(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteCancel = () => {
    setDocumentToDelete(null);
    setDeleteConfirmOpen(false);
  };

  const handleDelete = async () => {
    if (!documentToDelete) return;

    try {
      await deleteDocument(documentToDelete);
      setDocuments((prev) => prev.filter((doc) => doc.id !== documentToDelete));
    } catch (error) {
      console.error("Error deleting document:", error);
      setError("Failed to delete document. Please try again.");
    } finally {
      setDeleteConfirmOpen(false);
      setDocumentToDelete(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Management
      </Typography>

      {error && (
        <Paper
          sx={{
            p: 2,
            mb: 2,
            bgcolor: "error.light",
            color: "error.contrastText",
          }}
        >
          <Typography>{error}</Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Document
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<UploadFileIcon />}
                  fullWidth
                >
                  Select File
                  <input
                    type="file"
                    hidden
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileChange}
                  />
                </Button>
                {selectedFile && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Selected: {selectedFile.name} (
                    {formatFileSize(selectedFile.size)})
                  </Typography>
                )}
              </Box>

              <TextField
                label="Document Title"
                value={documentTitle}
                onChange={(e) => setDocumentTitle(e.target.value)}
                fullWidth
                margin="normal"
              />

              <TextField
                label="Document Type"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                fullWidth
                margin="normal"
                placeholder="Contract, Case Law, Statute, etc."
              />

              <TextField
                label="Jurisdiction"
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                fullWidth
                margin="normal"
                placeholder="Federal, California, New York, etc."
              />

              <TextField
                label="Document Date"
                type="date"
                value={documentDate}
                onChange={(e) => setDocumentDate(e.target.value)}
                fullWidth
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
              />

              <Button
                variant="contained"
                color="primary"
                onClick={handleUpload}
                disabled={uploading || !selectedFile}
                fullWidth
                sx={{ mt: 2 }}
              >
                {uploading ? <CircularProgress size={24} /> : "Upload Document"}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : documents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No documents found. Upload a document to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  documents.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>{doc.title || doc.filename}</TableCell>
                      <TableCell>{doc.document_type || "Unknown"}</TableCell>
                      <TableCell>{formatFileSize(doc.size)}</TableCell>
                      <TableCell>
                        <Chip
                          label={doc.status}
                          color={
                            doc.status === "processed"
                              ? "success"
                              : doc.status === "processing"
                              ? "warning"
                              : "error"
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          aria-label="delete"
                          onClick={() => handleDeleteConfirm(doc.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>

      <Dialog open={deleteConfirmOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this document? This action cannot be
            undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDelete} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents;
