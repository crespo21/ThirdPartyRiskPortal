import { Add as AddIcon } from '@mui/icons-material';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';
import React from 'react';

const Companies: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Companies</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Add Company
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Company Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This page will contain the company management interface with:
          </Typography>
          <ul>
            <li>Company listing with search and filters</li>
            <li>Add/Edit/Delete company functionality</li>
            <li>Company details and risk profiles</li>
            <li>Contact management</li>
            <li>Integration with Azure Storage for documents</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Companies; 