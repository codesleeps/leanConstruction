import React, { useState, useContext } from 'react';
import {
  Box, Paper, Typography, Button, Grid, Card, CardContent,
  Chip, Alert, CircularProgress, Dialog, DialogTitle,
  DialogContent, DialogActions, List, ListItem, ListItemIcon,
  ListItemText, Divider, Container
} from '@mui/material';
import {
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Construction as ConstructionIcon,
  Analytics as AnalyticsIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import axios from 'axios';
import { ColorModeContext } from '../App';

const API_BASE = import.meta.env.VITE_API_BASE || 'https://leanaiconstruction.com/api/v1';

const SignupPage = ({ onLogin, onSwitchToLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [demoDialogOpen, setDemoDialogOpen] = useState(false);
  const [createdDemoAccount, setCreatedDemoAccount] = useState(null);
  const colorMode = useContext(ColorModeContext);

  const demoAccountTypes = [
    {
      type: 'small',
      name: 'Small Contractor',
      description: 'Perfect for small construction companies with 3-10 projects',
      icon: <ConstructionIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      projectCount: '5-8 projects',
      sampleProjects: [
        'Residential Home Build',
        'Small Office Renovation',
        'Retail Store Construction'
      ],
      features: [
        'Basic waste tracking',
        'Project management',
        'Simple analytics',
        'Cost monitoring',
        'Timeline tracking'
      ],
      savings: '$50K - $150K per project',
      color: 'success'
    },
    {
      type: 'medium',
      name: 'Medium Builder',
      description: 'Ideal for growing construction businesses with 10-50 projects',
      icon: <BusinessIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      projectCount: '15-25 projects',
      sampleProjects: [
        'Commercial Building Phase 1',
        'Shopping Center Development',
        'Industrial Warehouse',
        'Office Complex'
      ],
      features: [
        'Advanced waste detection',
        'Team collaboration',
        'Detailed reporting',
        'Resource optimization',
        'Predictive analytics'
      ],
      savings: '$200K - $500K per project',
      color: 'warning'
    },
    {
      type: 'enterprise',
      name: 'Enterprise Client',
      description: 'Designed for large construction corporations with 50+ projects',
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: 'error.main' }} />,
      projectCount: '60-100+ projects',
      sampleProjects: [
        'Hospital Complex Construction',
        'Airport Terminal Expansion',
        'University Campus Development',
        'Skyscraper Project',
        'Infrastructure Network'
      ],
      features: [
        'AI-powered predictions',
        'Custom integrations',
        'White-label options',
        'Advanced analytics',
        'Multi-project oversight'
      ],
      savings: '$1M - $5M per project',
      color: 'error'
    }
  ];

  const handleCreateDemoAccount = async (accountType) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${API_BASE}/api/auth/demo-account/create?account_type=${accountType}`);

      const { demo_email, demo_password, message, account_type, login_url, features } = response.data;

      setCreatedDemoAccount({
        email: demo_email,
        password: demo_password,
        type: account_type,
        features: features
      });

      setSuccess(message);
      setDemoDialogOpen(true);

    } catch (error) {
      console.error('Demo account creation error:', error);
      setError(error.response?.data?.detail || 'Failed to create demo account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginWithDemo = () => {
    if (createdDemoAccount) {
      // Auto-login with demo credentials
      const demoUser = {
        id: 'demo-' + Date.now(),
        name: `Demo ${createdDemoAccount.type.charAt(0).toUpperCase() + createdDemoAccount.type.slice(1)} Manager`,
        email: createdDemoAccount.email,
        role: 'Project Manager',
        avatar: 'D'
      };

      localStorage.setItem('user', JSON.stringify(demoUser));
      localStorage.setItem('token', 'demo-jwt-token-' + Date.now());
      localStorage.setItem('demo_credentials', JSON.stringify(createdDemoAccount));

      onLogin(demoUser);
    }
  };

  const handleCloseDialog = () => {
    setDemoDialogOpen(false);
    setCreatedDemoAccount(null);
    setSuccess('');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4
      }}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6, position: 'relative' }}>
          <Button
            onClick={onSwitchToLogin}
            sx={{
              position: 'absolute',
              left: 0,
              top: 0,
              color: 'white',
              borderColor: 'white',
              '&:hover': {
                borderColor: 'white',
                bgcolor: 'rgba(255,255,255,0.1)'
              }
            }}
            variant="outlined"
            size="small"
          >
            ← Back to Login
          </Button>

          <Typography variant="h3" fontWeight="bold" color="white" gutterBottom>
            Try Lean AI Construction
          </Typography>
          <Typography variant="h6" color="white" sx={{ opacity: 0.9, mb: 2 }}>
            Experience the power of AI-driven construction waste detection
          </Typography>
          <Typography variant="body1" color="white" sx={{ opacity: 0.8 }}>
            Choose a demo account type that matches your business size and explore our platform with realistic construction data
          </Typography>
        </Box>

        {/* Error/Success Messages */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
            {error}
          </Alert>
        )}

        {success && !demoDialogOpen && (
          <Alert severity="success" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
            {success}
          </Alert>
        )}

        {/* Demo Account Cards */}
        <Grid container spacing={4} justifyContent="center">
          {demoAccountTypes.map((account) => (
            <Grid item xs={12} md={4} key={account.type}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: selectedAccount === account.type ? '2px solid' : '1px solid',
                  borderColor: selectedAccount === account.type ? `${account.color}.main` : 'divider',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: (theme) => theme.shadows[8],
                    borderColor: `${account.color}.main`
                  }
                }}
                onClick={() => setSelectedAccount(account.type)}
              >
                <CardContent sx={{ p: 3 }}>
                  {/* Header */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    {account.icon}
                    <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                      {account.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {account.description}
                    </Typography>
                    <Chip
                      label={account.projectCount}
                      color={account.color}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                  </Box>

                  {/* Sample Projects */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Sample Projects:
                    </Typography>
                    <List dense>
                      {account.sampleProjects.slice(0, 3).map((project, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <CheckCircleIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={project}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>

                  {/* Features */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Key Features:
                    </Typography>
                    <List dense>
                      {account.features.slice(0, 3).map((feature, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <CheckCircleIcon color="primary" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={feature}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>

                  {/* Savings */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography variant="h6" color={`${account.color}.main`} fontWeight="bold">
                      {account.savings}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Potential Savings Per Project
                    </Typography>
                  </Box>

                  {/* Create Button */}
                  <Button
                    variant="contained"
                    fullWidth
                    size="large"
                    color={account.color}
                    disabled={loading}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCreateDemoAccount(account.type);
                    }}
                    sx={{
                      py: 1.5,
                      fontSize: '1rem',
                      fontWeight: 600,
                      borderRadius: 2
                    }}
                  >
                    {loading ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : (
                      <>
                        Try {account.name} Demo
                        <ArrowForwardIcon sx={{ ml: 1 }} />
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Footer */}
        <Box sx={{ textAlign: 'center', mt: 6 }}>
          <Typography variant="body2" color="white" sx={{ opacity: 0.7 }}>
            All demo accounts include 7 days of full platform access with realistic construction data
          </Typography>
          <Typography variant="caption" color="white" sx={{ opacity: 0.5, mt: 1, display: 'block' }}>
            No credit card required • Full feature access • Professional support available
          </Typography>
        </Box>
      </Container>

      {/* Success Dialog */}
      <Dialog
        open={demoDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
          <Typography variant="h5" fontWeight="bold">
            Demo Account Created!
          </Typography>
        </DialogTitle>

        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3, textAlign: 'center' }}>
            Your demo account has been created with realistic construction data.
            You now have 7 days of full platform access.
          </Typography>

          {createdDemoAccount && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Your Demo Credentials:
              </Typography>
              <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Email:</strong> {createdDemoAccount.email}
                </Typography>
                <Typography variant="body2">
                  <strong>Password:</strong> {createdDemoAccount.password}
                </Typography>
              </Paper>

              <Typography variant="subtitle2" gutterBottom>
                Included Features:
              </Typography>
              <List dense>
                {createdDemoAccount.features?.map((feature, index) => (
                  <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <CheckCircleIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={feature}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Demo accounts expire after 7 days.</strong> All data will be automatically cleaned up.
            </Typography>
          </Alert>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={handleCloseDialog} sx={{ mr: 1 }}>
            View Credentials Later
          </Button>
          <Button
            variant="contained"
            onClick={handleLoginWithDemo}
            size="large"
            sx={{ px: 4 }}
          >
            Start Exploring
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SignupPage;