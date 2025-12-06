import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/projects/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const data = [
    { name: 'Defects', value: 15 },
    { name: 'Waiting', value: 20 },
    { name: 'Transportation', value: 10 },
    { name: 'Overproduction', value: 8 },
    { name: 'Inventory', value: 12 },
    { name: 'Motion', value: 18 },
    { name: 'Processing', value: 7 },
    { name: 'Talent', value: 5 },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Lean Construction Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* KPI Cards */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary">
              Active Projects
            </Typography>
            <Typography variant="h4">
              {projects.length}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary">
              Total Waste Detected
            </Typography>
            <Typography variant="h4">
              £125,000
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary">
              Efficiency Improvement
            </Typography>
            <Typography variant="h4">
              23%
            </Typography>
          </Paper>
        </Grid>

        {/* Waste Analysis Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              8 Wastes Analysis (DOWNTIME)
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Projects */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Recent Projects
            </Typography>
            {projects.slice(0, 5).map((project) => (
              <Box key={project.id} sx={{ mb: 1, p: 1, border: '1px solid #ddd', borderRadius: 1 }}>
                <Typography variant="subtitle1">{project.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {project.status} | Budget: £{project.budget.toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
