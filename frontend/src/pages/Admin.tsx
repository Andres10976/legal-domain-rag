import React, { useState, useEffect } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Slider,
  TextField,
  Typography,
} from '@mui/material';
import {
  getSystemStats,
  getSystemConfig,
  updateSystemConfig,
  reindexDocuments,
} from '../services/api';
import { SystemStats, SystemConfig } from '../types';

const Admin: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [updating, setUpdating] = useState<boolean>(false);
  const [reindexing, setReindexing] = useState<boolean>(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load system stats and config in parallel
      const [statsResponse, configResponse] = await Promise.all([
        getSystemStats(),
        getSystemConfig(),
      ]);
      
      setStats(statsResponse);
      setConfig(configResponse);
    } catch (error) {
      console.error('Error loading admin data:', error);
      setError('Failed to load system information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigUpdate = async () => {
    if (!config) return;
    
    try {
      setUpdating(true);
      setError(null);
      setSuccess(null);
      
      const updatedConfig = await updateSystemConfig(config);
      setConfig(updatedConfig);
      setSuccess('System configuration updated successfully.');
    } catch (error) {
      console.error('Error updating config:', error);
      setError('Failed to update system configuration. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleReindex = async () => {
    try {
      setReindexing(true);
      setError(null);
      setSuccess(null);
      
      await reindexDocuments();
      setSuccess('Reindexing started successfully. This process may take some time.');
    } catch (error) {
      console.error('Error starting reindex:', error);
      setError('Failed to start reindexing. Please try again.');
    } finally {
      setReindexing(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Administration
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Statistics
              </Typography>
              
              {stats && (
                <Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Document Count
                      </Typography>
                      <Typography variant="h5">
                        {stats.document_count}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total Chunks
                      </Typography>
                      <Typography variant="h5">
                        {stats.total_chunks}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Vector Store Size
                      </Typography>
                      <Typography variant="h5">
                        {stats.vector_store_size}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Avg. Query Time
                      </Typography>
                      <Typography variant="h5">
                        {stats.avg_query_time.toFixed(2)}s
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={loadData}
                  disabled={loading}
                  fullWidth
                >
                  Refresh Statistics
                </Button>
              </Box>
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Maintenance
              </Typography>
              
              <Typography variant="body2" paragraph color="text.secondary">
                Reindexing will process all documents again with the current configuration.
                This is useful after updating embeddings models or chunk settings.
              </Typography>
              
              <Button
                variant="contained"
                color="warning"
                onClick={handleReindex}
                disabled={reindexing}
                fullWidth
              >
                {reindexing ? <CircularProgress size={24} /> : 'Reindex All Documents'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Configuration
            </Typography>
            
            {config && (
              <Box>
                <FormControl fullWidth margin="normal">
                  <InputLabel>LLM Provider</InputLabel>
                  <Select
                    value={config.llm_provider}
                    label="LLM Provider"
                    onChange={(e) => setConfig({ ...config, llm_provider: e.target.value })}
                  >
                    <MenuItem value="anthropic">Anthropic (Claude)</MenuItem>
                    <MenuItem value="openai">OpenAI (GPT)</MenuItem>
                    <MenuItem value="google">Google (Gemini)</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal">
                  <InputLabel>Embedding Model</InputLabel>
                  <Select
                    value={config.embedding_model}
                    label="Embedding Model"
                    onChange={(e) => setConfig({ ...config, embedding_model: e.target.value })}
                  >
                    <MenuItem value="sentence-transformers/all-MiniLM-L6-v2">MiniLM-L6-v2 (Fast)</MenuItem>
                    <MenuItem value="sentence-transformers/all-mpnet-base-v2">MPNet (Balanced)</MenuItem>
                    <MenuItem value="text-embedding-ada-002">OpenAI Ada 002 (Accurate)</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal">
                  <InputLabel>Vector DB Provider</InputLabel>
                  <Select
                    value={config.vector_db_provider}
                    label="Vector DB Provider"
                    onChange={(e) => setConfig({ ...config, vector_db_provider: e.target.value })}
                  >
                    <MenuItem value="chroma">Chroma</MenuItem>
                    <MenuItem value="pinecone">Pinecone</MenuItem>
                    <MenuItem value="weaviate">Weaviate</MenuItem>
                  </Select>
                </FormControl>
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Chunk Size: {config.chunk_size}
                </Typography>
                <Slider
                  value={config.chunk_size}
                  min={250}
                  max={2000}
                  step={50}
                  onChange={(_, value) => setConfig({ ...config, chunk_size: value as number })}
                  valueLabelDisplay="auto"
                />
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Chunk Overlap: {config.chunk_overlap}
                </Typography>
                <Slider
                  value={config.chunk_overlap}
                  min={0}
                  max={500}
                  step={10}
                  onChange={(_, value) => setConfig({ ...config, chunk_overlap: value as number })}
                  valueLabelDisplay="auto"
                />
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Similarity Threshold: {config.similarity_threshold.toFixed(2)}
                </Typography>
                <Slider
                  value={config.similarity_threshold}
                  min={0.1}
                  max={0.9}
                  step={0.05}
                  onChange={(_, value) => setConfig({ ...config, similarity_threshold: value as number })}
                  valueLabelDisplay="auto"
                />
                
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleConfigUpdate}
                  disabled={updating}
                  fullWidth
                  sx={{ mt: 3 }}
                >
                  {updating ? <CircularProgress size={24} /> : 'Save Configuration'}
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Admin;
