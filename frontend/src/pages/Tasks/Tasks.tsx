import { Add as AddIcon } from '@mui/icons-material';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';
import React from 'react';

const Tasks: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Tasks</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Create Task
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Task Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This page will contain the task management interface with:
          </Typography>
          <ul>
            <li>Task creation and assignment</li>
            <li>Task status tracking and updates</li>
            <li>Due date management and notifications</li>
            <li>Task dependencies and workflows</li>
            <li>Integration with company and assessment data</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Tasks; 