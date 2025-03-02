import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Collapse,
  IconButton,
  Typography,
  Tooltip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { Citation as CitationType } from '../types';

interface CitationProps {
  citation: CitationType;
  index: number;
}

const Citation: React.FC<CitationProps> = ({ citation, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="subtitle1" component="div">
              [{index + 1}] {citation.document_title}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Relevance: {Math.round(citation.relevance_score * 100)}%
            </Typography>
          </Box>
          <Tooltip title={expanded ? "Show less" : "Show more"}>
            <IconButton
              onClick={() => setExpanded(!expanded)}
              aria-expanded={expanded}
              aria-label="show more"
              size="small"
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Tooltip>
        </Box>
        
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="body2">
              {citation.text}
            </Typography>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default Citation;
