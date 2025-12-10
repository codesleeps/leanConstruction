import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  AppBar, Toolbar, Typography, Container, Grid, Paper, Box,
  Tabs, Tab, Card, CardContent, CircularProgress, Chip,
  IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  LinearProgress, Alert, AlertTitle, TextField, Button, Avatar,
  Menu, MenuItem, Divider, Switch, FormControlLabel, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Warning as WarningIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Construction as ConstructionIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  Business as BusinessIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  Person as PersonIcon,
  Lock as LockIcon,
  Email as EmailIcon,
  Logout as LogoutIcon,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
         PieChart, Pie, Cell, RadarChart, Radar,
         PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import axios from 'axios';
import { StripePaymentProvider } from './components/StripePaymentContext';
import SubscriptionManager from './components/SubscriptionManager';
import Logo from './components/Logo';

const API_BASE = 'http://localhost:8000';

// Auth Context
const AuthContext = createContext(null);

const useAuth = () => useContext(AuthContext);

// Theme Context
const ColorModeContext = createContext({ toggleColorMode: () => {} });

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7300'];

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 3 }}>{children}</Box> : null;
}

// Login Component
function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('demo@leanconstruction.ai');
  const [password, setPassword] = useState('demo123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const colorMode = useContext(ColorModeContext);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Simulate API call
    setTimeout(() => {
      if (email && password) {
        const user = {
          id: '1',
          name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
          email: email,
          role: 'Project Manager',
          avatar: email.charAt(0).toUpperCase()
        };
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('token', 'demo-jwt-token-' + Date.now());
        onLogin(user);
      } else {
        setError('Please enter email and password');
      }
      setLoading(false);
    }, 1000);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('darkMode', (!darkMode).toString());
    colorMode.toggleColorMode();
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: darkMode 
          ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative'
      }}
    >
      {/* Dark Mode Toggle */}
      <IconButton
        onClick={handleDarkModeToggle}
        sx={{
          position: 'absolute',
          top: 20,
          right: 20,
          color: 'white',
          bgcolor: 'rgba(255,255,255,0.1)',
          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' }
        }}
      >
        {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
      </IconButton>

      <Container maxWidth="sm">
        <Paper
          elevation={24}
          sx={{
            p: 4,
            borderRadius: 3,
            bgcolor: darkMode ? 'rgba(30,30,46,0.95)' : 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(10px)'
          }}
        >
          {/* Logo Section */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
              <Logo size="large" variant="icon" sx={{ mb: 2 }} />
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Lean AI Construction
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to access your dashboard
              </Typography>
            </Box>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                boxShadow: '0 4px 14px rgba(25, 118, 210, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                }
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
            </Button>
          </form>

          {/* Demo Credentials */}
          <Box sx={{ mt: 3, p: 2, bgcolor: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block" textAlign="center">
              Demo Credentials
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" textAlign="center">
              Email: demo@leanconstruction.ai | Password: demo123
            </Typography>
          </Box>

          {/* Footer */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              © 2024 Lean AI Construction. All rights reserved.
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

// Main Dashboard Component
function Dashboard({ user, onLogout }) {
  const colorMode = useContext(ColorModeContext);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState(null);
  const [wasteData, setWasteData] = useState(null);
  const [kpiData, setKpiData] = useState(null);
  const [executiveSummary, setExecutiveSummary] = useState(null);
  const [industryData, setIndustryData] = useState(null);
  const [infrastructureStatus, setInfrastructureStatus] = useState(null);
  const [subscriptionTiers, setSubscriptionTiers] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);

  // Fallback data for when API is unavailable
  const fallbackIndustryData = {
    sectors: [
      { id: 'commercial', name: 'Commercial Construction', description: 'Office buildings, retail spaces, and commercial developments' },
      { id: 'residential', name: 'Residential Construction', description: 'Single-family homes, apartments, and housing developments' },
      { id: 'industrial', name: 'Industrial Construction', description: 'Factories, warehouses, and manufacturing facilities' },
      { id: 'infrastructure', name: 'Infrastructure', description: 'Roads, bridges, utilities, and public works' },
      { id: 'healthcare', name: 'Healthcare Facilities', description: 'Hospitals, clinics, and medical centers' },
      { id: 'education', name: 'Educational Facilities', description: 'Schools, universities, and training centers' }
    ]
  };

  const fallbackInfrastructureStatus = {
    infrastructure: {
      services: [
        { id: 'api', name: 'API Server', instances: 2, health: 'healthy' },
        { id: 'database', name: 'Database', instances: 1, health: 'healthy' },
        { id: 'cache', name: 'Redis Cache', instances: 1, health: 'healthy' },
        { id: 'ml', name: 'ML Engine', instances: 1, health: 'healthy' }
      ]
    }
  };

  const fallbackSubscriptionTiers = {
    tiers: [
      { id: 'free', name: 'Free', price_monthly: 0, projects: 1, users: 1, features: ['Basic waste analysis', 'Standard reports', 'Email support'] },
      { id: 'starter', name: 'Starter', price_monthly: 29, projects: 3, users: 5, features: ['Advanced analytics', 'Priority support', 'API access'] },
      { id: 'professional', name: 'Professional', price_monthly: 79, projects: 10, users: 20, features: ['Custom dashboards', 'Team collaboration', 'Integrations'] },
      { id: 'enterprise', name: 'Enterprise', price_monthly: 'Custom', projects: 'Unlimited', users: 'Unlimited', features: ['White-label', 'Dedicated support', 'Custom features'] }
    ]
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [healthRes, wasteRes, kpiRes, execRes, industryRes, infraRes, tiersRes] = await Promise.all([
        axios.get(`${API_BASE}/health`),
        axios.post(`${API_BASE}/api/v1/ml/analyze-waste`, {
          project_id: "demo-project",
          data: { schedule: [], budget: 2000000 },
          include_recommendations: true
        }),
        axios.get(`${API_BASE}/api/v1/ml/analytics/kpis/demo-project`),
        axios.get(`${API_BASE}/api/v1/ml/analytics/executive-summary/demo-project`),
        axios.get(`${API_BASE}/api/v1/ml/industry/sectors`),
        axios.get(`${API_BASE}/api/v1/ml/infrastructure/status`),
        axios.get(`${API_BASE}/api/v1/ml/commercial/tiers`)
      ]);

      setHealth(healthRes.data);
      setWasteData(wasteRes.data);
      setKpiData(kpiRes.data);
      setExecutiveSummary(execRes.data);
      setIndustryData(industryRes.data);
      setInfrastructureStatus(infraRes.data);
      setSubscriptionTiers(tiersRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('darkMode', (!darkMode).toString());
    colorMode.toggleColorMode();
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    onLogout();
  };

  const handleProfileClick = () => {
    handleMenuClose();
    setProfileDialogOpen(true);
  };

  const handleSettingsClick = () => {
    handleMenuClose();
    setSettingsDialogOpen(true);
  };

  // Use fallback data if API data is not available
  const displayIndustryData = industryData || fallbackIndustryData;
  const displayInfrastructureStatus = infrastructureStatus || fallbackInfrastructureStatus;
  const displaySubscriptionTiers = subscriptionTiers || fallbackSubscriptionTiers;

  const wasteChartData = wasteData ? Object.entries(wasteData.analysis?.wastes || {}).map(([name, data]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1).replace('_', ' '),
    score: Math.round(data.score * 100),
    cost: data.impact_cost
  })) : [];

  const kpiRadarData = kpiData ? [
    { metric: 'Schedule', value: kpiData.kpis?.schedule?.spi * 100 || 95 },
    { metric: 'Cost', value: kpiData.kpis?.cost?.cpi * 100 || 102 },
    { metric: 'Quality', value: kpiData.kpis?.quality?.first_time_quality * 100 || 94 },
    { metric: 'Safety', value: kpiData.kpis?.safety?.safety_compliance * 100 || 97 },
    { metric: 'Productivity', value: kpiData.kpis?.productivity?.labor_productivity * 100 || 91 }
  ] : [];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>Loading Dashboard...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={() => setDrawerOpen(!drawerOpen)} sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Logo size="small" variant="icon" sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            Lean AI Construction
          </Typography>
          
          {/* Dark Mode Toggle */}
          <IconButton color="inherit" onClick={handleDarkModeToggle} sx={{ mr: 1 }}>
            {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>

          <Chip 
            label={`v${health?.version || '4.0.0'}`} 
            size="small" 
            sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.2)', mr: 2 }}
          />

          {/* User Menu */}
          <IconButton color="inherit" onClick={handleMenuOpen}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36 }}>
              {user?.avatar || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle1" fontWeight="bold">{user?.name}</Typography>
              <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
              <Typography variant="caption" color="primary">{user?.role}</Typography>
            </Box>
            <Divider />
            <MenuItem onClick={handleProfileClick}>
              <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={handleSettingsClick}>
              <ListItemIcon><SettingsIcon fontSize="small" /></ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><LogoutIcon fontSize="small" color="error" /></ListItemIcon>
              <Typography color="error">Logout</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 240, mt: 8 } }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary">Welcome back,</Typography>
          <Typography variant="h6">{user?.name}</Typography>
        </Box>
        <Divider />
        <List>
          {[
            { text: 'Dashboard', icon: <DashboardIcon />, tab: 0 },
            { text: 'Waste Analysis', icon: <WarningIcon />, tab: 1 },
            { text: 'Analytics', icon: <AnalyticsIcon />, tab: 2 },
            { text: 'Industry', icon: <BusinessIcon />, tab: 3 },
            { text: 'Subscription', icon: <BusinessIcon />, tab: 4 },
            { text: 'System', icon: <SettingsIcon />, tab: 5 }
          ].map(({ text, icon, tab }) => (
            <ListItem button key={text} onClick={() => { setTabValue(tab); setDrawerOpen(false); }}>
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={text} />
            </ListItem>
          ))}
        </List>
        <Divider />
        <Box sx={{ p: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={handleDarkModeToggle}
                color="primary"
              />
            }
            label="Dark Mode"
          />
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Container maxWidth="xl">
          {/* Tabs */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} centered>
              <Tab icon={<DashboardIcon />} label="DASHBOARD" />
              <Tab icon={<WarningIcon />} label="WASTE ANALYSIS" />
              <Tab icon={<AnalyticsIcon />} label="ANALYTICS" />
              <Tab icon={<BusinessIcon />} label="INDUSTRY" />
              <Tab icon={<SettingsIcon />} label="SUBSCRIPTION" />
              <Tab icon={<SettingsIcon />} label="SYSTEM" />
            </Tabs>
          </Paper>

          {/* Dashboard Tab */}
          <TabPanel value={tabValue} index={0}>
            {/* Executive Summary Alert */}
            {executiveSummary && (
              <Alert 
                severity={executiveSummary.summary?.overall_health === 'GOOD' ? 'success' : 'warning'}
                sx={{ mb: 3 }}
              >
                <AlertTitle>Project Health: {executiveSummary.summary?.overall_health}</AlertTitle>
                Score: {executiveSummary.summary?.health_score}/100 — {executiveSummary.summary?.key_insights?.[0]}
              </Alert>
            )}

            {/* KPI Cards */}
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>Schedule Performance</Typography>
                        <Typography variant="h4">{kpiData?.kpis?.schedule?.spi?.toFixed(2) || '0.95'}</Typography>
                      </Box>
                      <SpeedIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(kpiData?.kpis?.schedule?.spi || 0.95) * 100} 
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>Cost Performance</Typography>
                        <Typography variant="h4">{kpiData?.kpis?.cost?.cpi?.toFixed(2) || '1.02'}</Typography>
                      </Box>
                      <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main' }} />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min((kpiData?.kpis?.cost?.cpi || 1.02) * 100, 100)} 
                      color="success"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>Quality Score</Typography>
                        <Typography variant="h4">{((kpiData?.kpis?.quality?.first_time_quality || 0.94) * 100).toFixed(0)}%</Typography>
                      </Box>
                      <CheckCircleIcon sx={{ fontSize: 40, color: 'info.main' }} />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(kpiData?.kpis?.quality?.first_time_quality || 0.94) * 100}
                      color="info"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>Safety Compliance</Typography>
                        <Typography variant="h4">{((kpiData?.kpis?.safety?.safety_compliance || 0.97) * 100).toFixed(0)}%</Typography>
                      </Box>
                      <AssessmentIcon sx={{ fontSize: 40, color: 'warning.main' }} />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(kpiData?.kpis?.safety?.safety_compliance || 0.97) * 100}
                      color="warning"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              {/* Performance Radar */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Performance Overview</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={kpiRadarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="metric" />
                      <PolarRadiusAxis angle={30} domain={[0, 120]} />
                      <Radar name="Performance" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    </RadarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>

              {/* Waste Summary */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Waste Impact (DOWNTIME)</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={wasteChartData}
                        dataKey="cost"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {wasteChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `£${value.toLocaleString()}`} />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Waste Analysis Tab */}
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <AlertTitle>DOWNTIME Framework</AlertTitle>
                  Analyzing 8 types of lean construction waste: Defects, Overproduction, Waiting, Non-utilized Talent, Transportation, Inventory, Motion, Extra Processing
                </Alert>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Waste Score by Category</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={wasteChartData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="name" type="category" width={120} />
                      <Tooltip />
                      <Bar dataKey="score" fill="#8884d8" name="Waste Score %" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Cost Impact Analysis</Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Waste Type</TableCell>
                          <TableCell align="right">Score</TableCell>
                          <TableCell align="right">Cost Impact</TableCell>
                          <TableCell align="right">Priority</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {wasteChartData.sort((a, b) => b.cost - a.cost).map((row, index) => (
                          <TableRow key={row.name}>
                            <TableCell>{row.name}</TableCell>
                            <TableCell align="right">{row.score}%</TableCell>
                            <TableCell align="right">£{row.cost.toLocaleString()}</TableCell>
                            <TableCell align="right">
                              <Chip 
                                label={index < 3 ? 'High' : index < 6 ? 'Medium' : 'Low'} 
                                color={index < 3 ? 'error' : index < 6 ? 'warning' : 'success'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>

              {wasteData?.analysis?.priority_actions && (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>Priority Actions</Typography>
                    {wasteData.analysis.priority_actions.map((action, index) => (
                      <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                        {action}
                      </Alert>
                    ))}
                  </Paper>
                </Grid>
              )}
            </Grid>
          </TabPanel>

          {/* Analytics Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              {executiveSummary?.summary?.key_insights?.map((insight, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Alert severity="info" icon={<TrendingUpIcon />}>
                    {insight}
                  </Alert>
                </Grid>
              ))}

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Risk Analysis</Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Risk Factor</TableCell>
                          <TableCell align="right">Probability</TableCell>
                          <TableCell align="right">Impact</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {executiveSummary?.summary?.risk_factors?.map((risk, index) => (
                          <TableRow key={index}>
                            <TableCell>{risk.risk}</TableCell>
                            <TableCell align="right">{(risk.probability * 100).toFixed(0)}%</TableCell>
                            <TableCell align="right">
                              <Chip 
                                label={risk.impact} 
                                color={risk.impact === 'HIGH' ? 'error' : risk.impact === 'MEDIUM' ? 'warning' : 'success'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Recommendations</Typography>
                  {executiveSummary?.summary?.recommendations?.map((rec, index) => (
                    <Alert key={index} severity="success" sx={{ mb: 1 }} icon={<CheckCircleIcon />}>
                      {rec}
                    </Alert>
                  ))}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Industry Tab */}
          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h5" gutterBottom>Supported Industry Sectors</Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Our platform supports various construction industry sectors with specialized tools and analytics.
                </Typography>
              </Grid>
              {displayIndustryData?.sectors?.map((sector) => (
                <Grid item xs={12} sm={6} md={4} key={sector.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <BusinessIcon sx={{ mr: 1, color: 'primary.main', fontSize: 32 }} />
                        <Typography variant="h6">{sector.name}</Typography>
                      </Box>
                      <Chip label={sector.id.toUpperCase()} size="small" color="primary" variant="outlined" sx={{ mb: 2 }} />
                      <Typography variant="body2" color="textSecondary">
                        {sector.description || 'Industry-specific KPIs, workflows, and compliance requirements'}
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="primary">
                          ✓ Custom KPIs ✓ Compliance Tools ✓ Industry Reports
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              
              {/* Industry Features Section */}
              <Grid item xs={12}>
                <Paper sx={{ p: 3, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Industry-Specific Features</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          📊 Custom Analytics
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Tailored metrics and KPIs specific to your industry sector for accurate performance tracking.
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          📋 Compliance Management
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Built-in compliance checklists and regulatory requirements for your construction sector.
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          🔧 Specialized Tools
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Industry-specific waste detection algorithms and optimization recommendations.
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Subscription Tab */}
          <TabPanel value={tabValue} index={4}>
            <SubscriptionManager user={user} />
          </TabPanel>

          {/* System Tab */}
          <TabPanel value={tabValue} index={5}>
            <Grid container spacing={3}>
              {/* Health Status */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>System Health</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                    <Typography>Status: {health?.status || 'Operational'}</Typography>
                  </Box>
                  <Typography variant="subtitle2" gutterBottom>Available Modules:</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {(health?.modules ? Object.entries(health.modules) : [
                      ['waste_detection', 'available'],
                      ['analytics', 'available'],
                      ['reporting', 'available'],
                      ['ml_engine', 'available'],
                      ['integrations', 'available']
                    ]).map(([name, status]) => (
                      <Chip
                        key={name}
                        label={name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        color={status === 'available' ? 'success' : 'error'}
                        size="small"
                      />
                    ))}
                  </Box>
                </Paper>
              </Grid>

              {/* Infrastructure */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Infrastructure</Typography>
                  {displayInfrastructureStatus?.infrastructure?.services?.map((service) => (
                    <Box key={service.id} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography>{service.name}</Typography>
                        <Chip
                          label={`${service.instances} instance${service.instances > 1 ? 's' : ''}`}
                          size="small"
                          color={service.health === 'healthy' ? 'success' : 'warning'}
                        />
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={service.health === 'healthy' ? 100 : 50}
                        color={service.health === 'healthy' ? 'success' : 'warning'}
                        sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Paper>
              </Grid>

              {/* Subscription Tiers */}
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>Subscription Plans</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Choose the plan that best fits your construction project needs.
                  </Typography>
                  <Grid container spacing={2}>
                    {displaySubscriptionTiers?.tiers?.map((tier, index) => (
                      <Grid item xs={12} sm={6} md={3} key={tier.id}>
                        <Card
                          variant="outlined"
                          sx={{
                            height: '100%',
                            border: index === 2 ? '2px solid' : '1px solid',
                            borderColor: index === 2 ? 'primary.main' : 'divider',
                            position: 'relative'
                          }}
                        >
                          {index === 2 && (
                            <Chip
                              label="Popular"
                              color="primary"
                              size="small"
                              sx={{ position: 'absolute', top: -10, right: 10 }}
                            />
                          )}
                          <CardContent>
                            <Typography variant="h6" color="primary" gutterBottom>{tier.name}</Typography>
                            <Typography variant="h4" fontWeight="bold">
                              {tier.price_monthly === 0 ? 'Free' :
                                typeof tier.price_monthly === 'number' ? `$${tier.price_monthly}` : tier.price_monthly}
                            </Typography>
                            {typeof tier.price_monthly === 'number' && tier.price_monthly > 0 && (
                              <Typography variant="caption" color="text.secondary">per month</Typography>
                            )}
                            <Divider sx={{ my: 2 }} />
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                              <strong>{tier.projects}</strong> projects • <strong>{tier.users}</strong> users
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                              {tier.features?.map((feature, idx) => (
                                <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                  <CheckCircleIcon sx={{ fontSize: 16, color: 'success.main', mr: 1 }} />
                                  <Typography variant="body2">{feature}</Typography>
                                </Box>
                              ))}
                            </Box>
                            <Button
                              variant={index === 2 ? "contained" : "outlined"}
                              fullWidth
                              sx={{ mt: 2 }}
                              onClick={() => setTabValue(4)}
                            >
                              {tier.price_monthly === 0 ? 'Get Started' : 'Upgrade'}
                            </Button>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </Grid>

              {/* System Information */}
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>System Information</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="primary">{health?.version || '4.0.0'}</Typography>
                        <Typography variant="body2" color="text.secondary">Platform Version</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="success.main">99.9%</Typography>
                        <Typography variant="body2" color="text.secondary">Uptime</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="info.main">&lt;100ms</Typography>
                        <Typography variant="body2" color="text.secondary">API Response</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="warning.main">24/7</Typography>
                        <Typography variant="body2" color="text.secondary">Monitoring</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </Container>
      </Box>

      {/* Profile Dialog */}
      <Dialog open={profileDialogOpen} onClose={() => setProfileDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>User Profile</DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mx: 'auto', mb: 2, bgcolor: 'primary.main', fontSize: 32 }}>
              {user?.avatar || 'U'}
            </Avatar>
            <Typography variant="h5" gutterBottom>{user?.name}</Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>{user?.email}</Typography>
            <Chip label={user?.role || 'User'} color="primary" sx={{ mt: 1 }} />
          </Box>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField fullWidth label="Full Name" defaultValue={user?.name} variant="outlined" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Email" defaultValue={user?.email} variant="outlined" disabled />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Role" defaultValue={user?.role} variant="outlined" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Company" defaultValue="Lean AI Construction" variant="outlined" />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setProfileDialogOpen(false)}>Save Changes</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsDialogOpen} onClose={() => setSettingsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <List>
            <ListItem>
              <ListItemIcon><DarkModeIcon /></ListItemIcon>
              <ListItemText primary="Dark Mode" secondary="Toggle dark/light theme" />
              <Switch checked={darkMode} onChange={handleDarkModeToggle} />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon><EmailIcon /></ListItemIcon>
              <ListItemText primary="Email Notifications" secondary="Receive project updates via email" />
              <Switch defaultChecked />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon><WarningIcon /></ListItemIcon>
              <ListItemText primary="Waste Alerts" secondary="Get notified about detected waste" />
              <Switch defaultChecked />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText primary="Weekly Reports" secondary="Receive weekly analytics summary" />
              <Switch defaultChecked />
            </ListItem>
          </List>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Data & Privacy</Typography>
          <List>
            <ListItem button>
              <ListItemText primary="Export My Data" secondary="Download all your project data" />
            </ListItem>
            <ListItem button>
              <ListItemText primary="Privacy Settings" secondary="Manage data sharing preferences" />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => setSettingsDialogOpen(false)}>Save Settings</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [mode, setMode] = useState(localStorage.getItem('darkMode') === 'true' ? 'dark' : 'light');

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [],
  );

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: '#1976d2' },
          secondary: { main: '#dc004e' },
          success: { main: '#4caf50' },
          warning: { main: '#ff9800' },
          error: { main: '#f44336' },
          ...(mode === 'dark' && {
            background: {
              default: '#0a1929',
              paper: '#0d2137',
            },
          }),
        },
        components: {
          MuiAppBar: {
            styleOverrides: {
              root: {
                background: mode === 'dark'
                  ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                  : 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
        },
      }),
    [mode],
  );

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <ColorModeContext.Provider value={colorMode}>
      <StripePaymentProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {user ? (
            <Dashboard user={user} onLogout={handleLogout} />
          ) : (
            <LoginPage onLogin={handleLogin} />
          )}
        </ThemeProvider>
      </StripePaymentProvider>
    </ColorModeContext.Provider>
  );
}

export default App;