import React from 'react';
import { Box, Button, Grid, Paper, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SettingsIcon from '@mui/icons-material/Settings';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h2" gutterBottom>
          Legal Domain RAG System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" paragraph>
          A specialized Retrieval-Augmented Generation system for legal documents, providing accurate, context-aware responses with proper citations.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              minHeight: 200,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 6,
              },
            }}
            onClick={() => navigate('/documents')}
          >
            <DescriptionIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Manage Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph align="center">
              Upload, view, and manage your legal documents. Our system supports PDF, DOCX, and TXT formats.
            </Typography>
            <Button variant="contained" color="primary">
              Go to Documents
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              minHeight: 200,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 6,
              },
            }}
            onClick={() => navigate('/query')}
          >
            <QuestionAnswerIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Ask Questions
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph align="center">
              Query your legal documents using natural language. Get accurate answers with proper citations to source material.
            </Typography>
            <Button variant="contained" color="primary">
              Go to Query
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              minHeight: 200,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 6,
              },
            }}
            onClick={() => navigate('/admin')}
          >
            <SettingsIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              System Administration
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph align="center">
              Configure system settings, view statistics, and manage the document corpus.
            </Typography>
            <Button variant="contained" color="primary">
              Go to Admin
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 6, p: 3, bgcolor: 'background.paper', borderRadius: 1 }}>
        <Typography variant="h4" gutterBottom>
          About This System
        </Typography>
        <Typography variant="body1" paragraph>
          The Legal Domain RAG System combines advanced natural language processing with specialized legal knowledge to provide accurate, context-aware responses to your legal queries.
        </Typography>
        <Typography variant="body1" paragraph>
          Our system is designed specifically for legal professionals, with features tailored to the unique requirements of legal research and analysis.
        </Typography>
        <Typography variant="body1" paragraph>
          Upload your documents, ask questions in plain language, and receive answers with proper citations to the relevant sections of your documents.
        </Typography>
      </Box>
    </Box>
  );
};

export default Home;
