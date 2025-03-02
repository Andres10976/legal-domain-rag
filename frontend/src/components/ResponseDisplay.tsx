import React, { useState } from 'react';
import {
  Box,
  Chip,
  Divider,
  Paper,
  Tooltip,
  Typography,
} from '@mui/material';
import { QueryResponse } from '../types';
import Citation from './Citation';

interface ResponseDisplayProps {
  response: QueryResponse;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ response }) => {
  const [activeCitation, setActiveCitation] = useState<string | null>(null);

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.5) return 'warning';
    return 'error';
  };

  const renderResponseWithCitations = (text: string) => {
    // Regular expression to find citation markers like [1], [2], etc.
    const parts = text.split(/(\[\d+\])/g);
    
    return parts.map((part, index) => {
      const citationMatch = part.match(/\[(\d+)\]/);
      
      if (citationMatch) {
        const citationIndex = parseInt(citationMatch[1]) - 1;
        if (citationIndex >= 0 && citationIndex < response.citations.length) {
          return (
            <Tooltip key={index} title={`Click to view source: ${response.citations[citationIndex].document_title}`}>
              <Box 
                component="span" 
                sx={{ 
                  color: 'primary.main', 
                  cursor: 'pointer',
                  fontWeight: 'medium',
                  '&:hover': { textDecoration: 'underline' } 
                }}
                onClick={() => setActiveCitation(response.citations[citationIndex].chunk_id)}
              >
                {part}
              </Box>
            </Tooltip>
          );
        }
      }
      
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Response</Typography>
          <Tooltip title="System confidence in this answer">
            <Chip
              label={`Confidence: ${Math.round(response.confidence_score * 100)}%`}
              color={getConfidenceColor(response.confidence_score)}
              size="small"
            />
          </Tooltip>
        </Box>
        
        <Typography variant="body1" component="div">
          {renderResponseWithCitations(response.response)}
        </Typography>
      </Paper>
      
      <Typography variant="h6" gutterBottom>
        Sources ({response.citations.length})
      </Typography>
      
      {response.citations.map((citation, index) => (
        <Citation 
          key={citation.chunk_id} 
          citation={citation} 
          index={index}
        />
      ))}
    </Box>
  );
};

export default ResponseDisplay;
