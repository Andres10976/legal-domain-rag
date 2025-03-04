import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Collapse,
  Divider,
  IconButton,
  Paper,
  Typography,
  useTheme,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { QueryResponse } from "../types";

interface ResponseDisplayProps {
  response: QueryResponse;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ response }) => {
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const theme = useTheme();

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return theme.palette.success.main;
    if (score >= 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const renderResponseWithCitations = (text: string) => {
    // Enhanced citation regex to handle various formats like [1], [Source 1], etc.
    const parts = text.split(/(\[[^\]]*\d+[^\]]*\])/g);

    return parts.map((part, index) => {
      // Check if this part is a citation reference
      const citationMatch = part.match(/\[(?:[^\]]*)?(\d+)(?:[^\]]*)?]/);

      if (citationMatch) {
        const citationIndex = parseInt(citationMatch[1]) - 1;
        if (citationIndex >= 0 && citationIndex < response.citations.length) {
          return (
            <Box
              key={index}
              component="span"
              sx={{
                color: "primary.main",
                cursor: "pointer",
                fontWeight: "medium",
                "&:hover": { textDecoration: "underline" },
                display: "inline-flex",
                alignItems: "center",
              }}
              onClick={() =>
                setExpandedCitation(response.citations[citationIndex].chunk_id)
              }
            >
              {part}
            </Box>
          );
        }
      }

      return <span key={index}>{part}</span>;
    });
  };

  return (
    <Box>
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 3,
          borderLeft: `4px solid ${getConfidenceColor(
            response.confidence_score
          )}`,
          borderRadius: "4px 4px 4px 4px",
        }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h6" color="primary" fontWeight="bold">
            Response
          </Typography>
          <Chip
            label={`Confidence: ${Math.round(
              response.confidence_score * 100
            )}%`}
            sx={{
              color: "white",
              bgcolor: getConfidenceColor(response.confidence_score),
            }}
            size="small"
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Typography
          variant="body1"
          component="div"
          sx={{
            fontSize: "1.05rem",
            lineHeight: 1.6,
          }}
        >
          {renderResponseWithCitations(response.response)}
        </Typography>
      </Paper>

      <Typography variant="h6" gutterBottom color="primary">
        Sources ({response.citations.length})
      </Typography>

      {response.citations.map((citation, index) => (
        <Card
          key={citation.chunk_id}
          sx={{
            mb: 2,
            borderLeft: "4px solid",
            borderColor: "primary.light",
            "&:hover": { boxShadow: 3 },
          }}
        >
          <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Box>
                <Typography variant="subtitle1" fontWeight="medium">
                  [{index + 1}] {citation.document_title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Relevance: {Math.round(citation.relevance_score * 100)}%
                </Typography>
              </Box>
              <IconButton
                onClick={() =>
                  setExpandedCitation(
                    expandedCitation === citation.chunk_id
                      ? null
                      : citation.chunk_id
                  )
                }
                size="small"
                sx={{
                  bgcolor:
                    expandedCitation === citation.chunk_id
                      ? "primary.light"
                      : "transparent",
                  color:
                    expandedCitation === citation.chunk_id
                      ? "white"
                      : "inherit",
                  "&:hover": {
                    bgcolor:
                      expandedCitation === citation.chunk_id
                        ? "primary.main"
                        : "primary.light",
                    color: "white",
                  },
                }}
              >
                {expandedCitation === citation.chunk_id ? (
                  <ExpandLessIcon />
                ) : (
                  <ExpandMoreIcon />
                )}
              </IconButton>
            </Box>

            <Collapse
              in={expandedCitation === citation.chunk_id}
              timeout="auto"
              unmountOnExit
            >
              <Box
                sx={{
                  mt: 2,
                  p: 2,
                  bgcolor: "background.default",
                  borderRadius: 1,
                  fontSize: "0.95rem",
                  whiteSpace: "pre-wrap",
                  maxHeight: "300px",
                  overflow: "auto",
                  borderLeft: "3px solid",
                  borderColor: "primary.light",
                }}
              >
                <Typography variant="body2">{citation.text}</Typography>
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default ResponseDisplay;
