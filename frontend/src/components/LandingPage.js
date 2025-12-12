import React, { useContext } from 'react';
import {
  Box, Button, Container, Grid, Paper, Typography, Card, CardContent,
  Chip, IconButton, Avatar, Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Construction as ConstructionIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  Business as BusinessIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  Person as PersonIcon,
  Lock as LockIcon,
  Email as EmailIcon
} from '@mui/icons-material';
import { ColorModeContext } from '../App';
import Logo from './Logo';

function LandingPage({ onSwitchToSignup, onSwitchToLogin }) {
  const colorMode = useContext(ColorModeContext);
  const darkMode = localStorage.getItem('darkMode') === 'true';

  const handleDarkModeToggle = () => {
    const newMode = !darkMode;
    localStorage.setItem('darkMode', newMode.toString());
    colorMode.toggleColorMode();
  };

  const features = [
    {
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Waste Detection & Analytics',
      description: 'AI-powered analysis of construction waste using the DOWNTIME framework to identify 8 types of lean waste.'
    },
    {
      icon: <ConstructionIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      title: 'Industry-Specific Tools',
      description: 'Tailored solutions for commercial, residential, industrial, infrastructure, healthcare, and education sectors.'
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      title: 'Real-Time Monitoring',
      description: 'Continuous project monitoring with predictive analytics to prevent delays and cost overruns.'
    },
    {
      icon: <AssessmentIcon sx={{ fontSize: 40, color: 'info.main' }} />,
      title: 'Performance KPIs',
      description: 'Comprehensive dashboard with schedule performance, cost control, quality metrics, and safety compliance.'
    },
    {
      icon: <BusinessIcon sx={{ fontSize: 40, color: 'secondary.main' }} />,
      title: 'ERP Integrations',
      description: 'Seamless integration with Procore, IoT sensors, and other construction management platforms.'
    },
    {
      icon: <CheckCircleIcon sx={{ fontSize: 40, color: 'error.main' }} />,
      title: 'Compliance Management',
      description: 'Built-in regulatory compliance tools and automated reporting for construction standards.'
    }
  ];

  const logos = [
    '/trustedByLeadingCompanies/Aecom-logo.webp',
    '/trustedByLeadingCompanies/BLACKRIDGE+1-528w.webp',
    '/trustedByLeadingCompanies/Hensel_Phelps_200_200.webp',
    '/trustedByLeadingCompanies/IC-Case-Study-Featured-Image-Kier-Construction-Logo-IC-700x299.webp',
    '/trustedByLeadingCompanies/iso-ce-web-2024-600x205-1.webp',
    '/trustedByLeadingCompanies/logo.webp',
    '/trustedByLeadingCompanies/network-rail-logo-png_seeklogo-323728.webp'
  ];

  const integrations = [
    { name: "Procore", logo: "/integrated_tools_logo/procore.webp" },
    { name: "Autodesk", logo: "/integrated_tools_logo/autodesk.webp" },
    { name: "Microsoft Project", logo: "/integrated_tools_logo/microsoft-project.webp" },
    { name: "Primavera P6", logo: "/integrated_tools_logo/Primavera-P6.webp" },
    { name: "Bluebeam", logo: "/integrated_tools_logo/Bluebeam.webp" },
    { name: "PlanGrid", logo: "/integrated_tools_logo/plangrid-logo.webp" },
    { name: "Sage", logo: "/integrated_tools_logo/sage.webp" },
    { name: "QuickBooks", logo: "/integrated_tools_logo/intuit-quickbooks.webp" },
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Project Manager',
      company: 'Aecom',
      avatar: 'SJ',
      text: 'Lean AI Construction transformed our project efficiency. We reduced waste by 35% in the first quarter.'
    },
    {
      name: 'Mike Chen',
      role: 'Operations Director',
      company: 'Kier Construction',
      avatar: 'MC',
      text: 'The predictive analytics helped us avoid costly delays. Highly recommend for any construction firm.'
    },
    {
      name: 'Emma Rodriguez',
      role: 'Lean Manager',
      company: 'Network Rail',
      avatar: 'ER',
      text: 'Finally, a tool that understands construction waste. The DOWNTIME framework is game-changing.'
    }
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: darkMode
          ? 'linear-gradient(135deg, #0a1929 0%, #16213e 50%, #1a1a2e 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
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
          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
          zIndex: 1000
        }}
      >
        {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
      </IconButton>

      {/* Navigation Bar */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255,255,255,0.2)'
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Logo size="small" variant="icon" sx={{ mr: 2 }} />
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                Lean AI Construction
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="text"
                sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}
                onClick={onSwitchToLogin}
              >
                Sign In
              </Button>
              <Button
                variant="contained"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                }}
                onClick={onSwitchToSignup}
              >
                Get Started
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ pt: 12, pb: 8 }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography
              variant="h2"
              sx={{
                color: 'white',
                fontWeight: 'bold',
                mb: 3,
                fontSize: { xs: '2.5rem', md: '3.5rem' }
              }}
            >
              Transform Construction
              <br />
              with AI-Powered
              <br />
              Lean Management
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: 'rgba(255,255,255,0.9)',
                mb: 4,
                lineHeight: 1.6
              }}
            >
              Eliminate waste, optimize performance, and deliver projects on time with our advanced AI platform.
              Supporting all major construction sectors with industry-specific tools.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                  boxShadow: '0 4px 14px rgba(25, 118, 210, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                  }
                }}
                endIcon={<ArrowForwardIcon />}
                onClick={onSwitchToSignup}
              >
                Start Free Trial
              </Button>
              <Button
                variant="outlined"
                size="large"
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  borderColor: 'white',
                  color: 'white',
                  '&:hover': {
                    borderColor: 'white',
                    bgcolor: 'rgba(255,255,255,0.1)',
                  }
                }}
                onClick={onSwitchToLogin}
              >
                Sign In
              </Button>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={24}
              sx={{
                p: 4,
                borderRadius: 3,
                bgcolor: darkMode ? 'rgba(30,30,46,0.95)' : 'rgba(255,255,255,0.95)',
                backdropFilter: 'blur(10px)',
                textAlign: 'center'
              }}
            >
              <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                35% Average Waste Reduction
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Our clients see immediate improvements in project efficiency and cost savings.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Chip label="AI-Powered" color="primary" />
                <Chip label="Real-Time" color="success" />
                <Chip label="Industry-Leading" color="warning" />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.1)', py: 8 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            sx={{
              textAlign: 'center',
              mb: 2,
              fontWeight: 'bold',
              color: darkMode ? 'white' : 'text.primary'
            }}
          >
            Powerful Features for Modern Construction
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              mb: 6,
              color: darkMode ? 'rgba(255,255,255,0.7)' : 'text.secondary'
            }}
          >
            Everything you need to optimize your construction projects
          </Typography>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: darkMode ? 'rgba(30,30,46,0.8)' : 'rgba(255,255,255,0.9)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    transition: 'transform 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ mb: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Integrations Section */}
      <Box sx={{ bgcolor: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.1)', py: 8 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            sx={{
              textAlign: 'center',
              mb: 2,
              fontWeight: 'bold',
              color: darkMode ? 'white' : 'text.primary'
            }}
          >
            Integrates with your favorite tools
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              mb: 6,
              color: darkMode ? 'rgba(255,255,255,0.7)' : 'text.secondary'
            }}
          >
            Seamlessly connect with the construction software you already use
          </Typography>
          <Grid container spacing={4}>
            {integrations.map((integration, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Paper
                  elevation={3}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    bgcolor: darkMode ? 'rgba(30,30,46,0.8)' : 'rgba(255,255,255,0.9)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  <img
                    src={integration.logo}
                    alt={integration.name}
                    style={{
                      height: '64px',
                      width: 'auto',
                      maxWidth: '100%',
                      margin: '0 auto 12px auto',
                      objectFit: 'contain',
                      display: 'block'
                    }}
                    loading="lazy"
                  />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: darkMode ? 'white' : 'text.primary' }}>
                    {integration.name}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          sx={{
            textAlign: 'center',
            mb: 2,
            fontWeight: 'bold',
            color: 'white'
          }}
        >
          Trusted by Leading Construction Companies
        </Typography>
        <Typography
          variant="h6"
          sx={{
            textAlign: 'center',
            mb: 6,
            color: 'rgba(255,255,255,0.7)'
          }}
        >
          See what industry leaders say about our platform
        </Typography>
        <Grid container spacing={4}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Paper
                sx={{
                  p: 3,
                  borderRadius: 3,
                  bgcolor: darkMode ? 'rgba(30,30,46,0.9)' : 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  height: '100%'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    {testimonial.avatar}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {testimonial.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {testimonial.role} at {testimonial.company}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                  "{testimonial.text}"
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ bgcolor: 'rgba(255,255,255,0.1)', py: 8 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography
            variant="h3"
            sx={{
              mb: 3,
              fontWeight: 'bold',
              color: 'white'
            }}
          >
            Ready to Transform Your Construction Projects?
          </Typography>
          <Typography
            variant="h6"
            sx={{
              mb: 4,
              color: 'rgba(255,255,255,0.8)',
              maxWidth: 600,
              mx: 'auto'
            }}
          >
            Join thousands of construction professionals using AI to eliminate waste and deliver projects on time.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              sx={{
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 'bold',
                background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                boxShadow: '0 4px 14px rgba(25, 118, 210, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                }
              }}
              endIcon={<ArrowForwardIcon />}
              onClick={onSwitchToSignup}
            >
              Start Your Free Trial
            </Button>
            <Button
              variant="outlined"
              size="large"
              sx={{
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                borderColor: 'white',
                color: 'white',
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255,255,255,0.1)',
                }
              }}
              onClick={onSwitchToLogin}
            >
              Sign In to Dashboard
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: 'rgba(0,0,0,0.2)', py: 4 }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: { xs: 2, md: 0 } }}>
              <Logo size="small" variant="icon" sx={{ mr: 2 }} />
              <Typography variant="body1" sx={{ color: 'white', fontWeight: 'bold' }}>
                Lean AI Construction
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              © 2024 Lean AI Construction. All rights reserved.
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}

export default LandingPage;