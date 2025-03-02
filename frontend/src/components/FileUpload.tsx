import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { uploadDocument } from '../services/api';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [date, setDate] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
      
      // Use file name as default title if no title is set
      if (!title) {
        setTitle(selectedFile.name);
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccess(null);

      const formData = new FormData();
      formData.append('file', file);
      
      if (title) {
        formData.append('title', title);
      }
      
      if (documentType) {
        formData.append('document_type', documentType);
      }
      
      if (jurisdiction) {
        formData.append('jurisdiction', jurisdiction);
      }
      
      if (date) {
        formData.append('date', date);
      }

      const response = await uploadDocument(formData);
      
      setSuccess(`Document uploaded successfully. ID: ${response.id}`);
      onUploadSuccess();
      
      // Reset form
      setFile(null);
      setTitle('');
      setDocumentType('');
      setJurisdiction('');
      setDate('');
      
      // Clear file input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      setError('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Upload Legal Document
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <Box sx={{ mb: 3 }}>
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadFileIcon />}
            fullWidth
          >
            Select File
            <input
              id="file-upload"
              type="file"
              hidden
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
            />
          </Button>
          
          {file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected: {file.name} ({formatFileSize(file.size)})
            </Typography>
          )}
        </Box>
        
        <TextField
          label="Document Title"
          fullWidth
          margin="normal"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          variant="outlined"
        />
        
        <TextField
          label="Document Type"
          fullWidth
          margin="normal"
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          variant="outlined"
          placeholder="Contract, Statute, Case, etc."
        />
        
        <TextField
          label="Jurisdiction"
          fullWidth
          margin="normal"
          value={jurisdiction}
          onChange={(e) => setJurisdiction(e.target.value)}
          variant="outlined"
          placeholder="Federal, California, New York, etc."
        />
        
        <TextField
          label="Document Date"
          type="date"
          fullWidth
          margin="normal"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          variant="outlined"
          InputLabelProps={{
            shrink: true,
          }}
        />
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={uploading || !file}
          fullWidth
          sx={{ mt: 2 }}
        >
          {uploading ? <CircularProgress size={24} /> : 'Upload Document'}
        </Button>
        
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Supported formats: PDF, DOCX, TXT
        </Typography>
      </CardContent>
    </Card>
  );
};

export default FileUpload;
