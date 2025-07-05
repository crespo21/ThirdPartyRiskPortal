import {
    Assessment,
    Assignment,
    Business,
    CheckCircle,
    Description,
    Schedule,
    TrendingUp,
    Warning,
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    Chip,
    Grid,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Paper,
    Typography,
} from '@mui/material';
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

// Mock data - replace with actual API calls
const mockData = {
  totalCompanies: 156,
  activeAssessments: 23,
  pendingTasks: 45,
  dueDiligenceRequests: 12,
  riskDistribution: {
    low: 45,
    medium: 67,
    high: 32,
    critical: 12,
  },
  recentActivities: [
    { id: 1, type: 'Assessment', company: 'TechCorp Inc.', status: 'Completed', time: '2 hours ago' },
    { id: 2, type: 'Due Diligence', company: 'Global Solutions', status: 'Pending', time: '4 hours ago' },
    { id: 3, type: 'Task', company: 'Innovation Labs', status: 'In Progress', time: '6 hours ago' },
    { id: 4, type: 'Assessment', company: 'DataFlow Systems', status: 'Scheduled', time: '1 day ago' },
  ],
};

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}> = ({ title, value, icon, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: 2,
            p: 1,
            mr: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="h4" component="div" fontWeight="bold">
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
        </Box>
      </Box>
      {subtitle && (
        <Typography variant="caption" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const RiskLevelCard: React.FC = () => {
  const { riskDistribution } = mockData;
  const total = Object.values(riskDistribution).reduce((sum, val) => sum + val, 0);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'high': return '#f44336';
      case 'critical': return '#9c27b0';
      default: return '#757575';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Risk Distribution
        </Typography>
        {Object.entries(riskDistribution).map(([level, count]) => (
          <Box key={level} sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                {level} Risk
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {count} ({((count / total) * 100).toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(count / total) * 100}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getRiskColor(level),
                },
              }}
            />
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

const RecentActivityCard: React.FC = () => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle color="success" />;
      case 'Pending':
        return <Schedule color="warning" />;
      case 'In Progress':
        return <TrendingUp color="info" />;
      case 'Scheduled':
        return <Schedule color="primary" />;
      default:
        return <Warning color="error" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'success';
      case 'Pending': return 'warning';
      case 'In Progress': return 'info';
      case 'Scheduled': return 'primary';
      default: return 'error';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <List>
          {mockData.recentActivities.map((activity) => (
            <ListItem key={activity.id} sx={{ px: 0 }}>
              <ListItemIcon>
                {getStatusIcon(activity.status)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" fontWeight="medium">
                      {activity.type}
                    </Typography>
                    <Chip
                      label={activity.status}
                      size="small"
                      color={getStatusColor(activity.status) as any}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {activity.company}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {activity.time}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Welcome back, {user?.full_name || user?.username}! Here's an overview of your TPRM activities.
      </Typography>

      <Grid container spacing={3}>
        {/* Stat Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Companies"
            value={mockData.totalCompanies}
            icon={<Business sx={{ color: 'white' }} />}
            color="#1976d2"
            subtitle="Under management"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Assessments"
            value={mockData.activeAssessments}
            icon={<Assessment sx={{ color: 'white' }} />}
            color="#2e7d32"
            subtitle="In progress"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Tasks"
            value={mockData.pendingTasks}
            icon={<Assignment sx={{ color: 'white' }} />}
            color="#ed6c02"
            subtitle="Require attention"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Due Diligence"
            value={mockData.dueDiligenceRequests}
            icon={<Description sx={{ color: 'white' }} />}
            color="#9c27b0"
            subtitle="Awaiting review"
          />
        </Grid>

        {/* Risk Distribution */}
        <Grid item xs={12} md={6}>
          <RiskLevelCard />
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <RecentActivityCard />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                    }}
                  >
                    <Business sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                    <Typography variant="body2">Add Company</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                    }}
                  >
                    <Assessment sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                    <Typography variant="body2">Start Assessment</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                    }}
                  >
                    <Assignment sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                    <Typography variant="body2">Create Task</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                    }}
                  >
                    <Description sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
                    <Typography variant="body2">Upload Document</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 