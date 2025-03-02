import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
  IconButton,
  Paper,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ReactMarkdown from 'react-markdown';
import { queryDocuments, getHistory } from '../services/api';
import { Citation, QueryResponse, HistoryItem } from '../types';

const Query: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyOpen, setHistoryOpen] = useState<boolean>(false);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const responseRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await getHistory();
      setHistory(response.history);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await queryDocuments({
        query: query.trim(),
      });
      
      setResponse(response);
      
      // Scroll to response
      if (responseRef.current) {
        responseRef.current.scrollIntoView({ behavior: 'smooth' });
      }
      
    } catch (error) {
      console.error('Error querying documents:', error);
      setError('Failed to process your query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (item: HistoryItem) => {
    setQuery(item.query);
  };

  const toggleCitation = (citationId: string) => {
    if (expandedCitation === citationId) {
      setExpandedCitation(null);
    } else {
      setExpandedCitation(citationId);
    }
  };

  const renderResponseWithCitations = (text: string, citations: Citation[]) => {
    // This is a simple implementation
    // In a real app, we would use more sophisticated citation rendering
    let renderedText = text;
    
    // Replace citation markers with clickable spans
    const citationPattern = /\[(\d+)\]/g;
    renderedText = renderedText.replace(citationPattern, (match, citationNum) => {
      const index = parseInt(citationNum) - 1;
      if (index >= 0 && index < citations.length) {
        return `<span class="citation" data-citation-id="${citations[index].chunk_id}">[${citationNum}]</span>`;
      }
      return match;
    });
    
    return (
      <div
        dangerouslySetInnerHTML={{ __html: renderedText }}
        onClick={(e) => {
          const target = e.target as HTMLElement;
          if (target.classList.contains('citation')) {
            const citationId = target.getAttribute('data-citation-id');
            if (citationId) {
              toggleCitation(citationId);
            }
          }
        }}
      />
    );
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.5) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        Query Legal Documents
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Button
          startIcon={historyOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setHistoryOpen(!historyOpen)}
        >
          {historyOpen ? 'Hide History' : 'Show History'}
        </Button>
        
        <Collapse in={historyOpen}>
          <Paper sx={{ mt: 1, p: 2, maxHeight: '200px', overflow: 'auto' }}>
            {history.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No query history yet.
              </Typography>
            ) : (
              history.map((item, index) => (
                <Box key={index} sx={{ mb: 1 }}>
                  <Button
                    variant="text"
                    onClick={() => handleHistoryClick(item)}
                    sx={{ textAlign: 'left', textTransform: 'none' }}
                    fullWidth
                  >
                    <Typography noWrap sx={{ width: '100%' }}>
                      {item.query}
                    </Typography>
                  </Button>
                  <Divider />
                </Box>
              ))
            )}
          </Paper>
        </Collapse>
      </Box>
      
      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>{error}</Typography>
        </Paper>
      )}
      
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          mb: 2,
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      >
        <Box
          ref={responseRef}
          sx={{
            flexGrow: 1,
            p: 2,
            overflowY: 'auto',
            bgcolor: response ? 'background.paper' : 'background.default',
          }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : response ? (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Response</Typography>
                <Tooltip title="Confidence Score">
                  <Chip
                    label={`Confidence: ${Math.round(response.confidence_score * 100)}%`}
                    color={getConfidenceColor(response.confidence_score)}
                    size="small"
                  />
                </Tooltip>
              </Box>
              
              <Typography component="div" variant="body1" sx={{ mb: 2 }}>
                {renderResponseWithCitations(response.response, response.citations)}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Sources
              </Typography>
              
              {response.citations.map((citation, index) => (
                <Card key={citation.chunk_id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="subtitle1">
                        [{index + 1}] {citation.document_title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => toggleCitation(citation.chunk_id)}
                      >
                        {expandedCitation === citation.chunk_id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                    
                    <Collapse in={expandedCitation === citation.chunk_id}>
                      <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                        <Typography variant="body2">{citation.text}</Typography>
                      </Box>
                    </Collapse>
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Typography variant="body1" color="text.secondary">
                Ask a question about your legal documents to get started.
              </Typography>
            </Box>
          )}
        </Box>
        
        <Divider />
        
        <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex' }}>
              <TextField
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a legal question..."
                fullWidth
                variant="outlined"
                disabled={loading}
                autoFocus
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                disabled={loading || !query.trim()}
                sx={{ ml: 1 }}
              >
                Ask
              </Button>
            </Box>
          </form>
        </Box>
      </Box>
    </Box>
  );
};

export default Query;
