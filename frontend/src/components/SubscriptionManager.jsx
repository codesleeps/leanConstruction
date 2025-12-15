import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  Star,
  LocalOffer,
  Payment,
  Cancel
} from '@mui/icons-material';
import PaymentForm from './PaymentForm';
import { useStripePayment } from './StripePaymentContext';

const SubscriptionManager = ({ user }) => {
  const {
    subscription,
    loading,
    createSubscription,
    cancelSubscription,
    getSubscriptionStatus
  } = useStripePayment();
  
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);

  // Subscription plans
  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 29,
      description: 'Perfect for small construction projects',
      features: [
        'Up to 3 projects',
        'Basic waste analysis',
        'Standard reports',
        'Email support'
      ],
      color: 'primary',
      popular: false
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 79,
      description: 'Ideal for growing construction businesses',
      features: [
        'Up to 10 projects',
        'Advanced waste detection',
        'Custom analytics',
        'Priority support',
        'API access',
        'Team collaboration'
      ],
      color: 'secondary',
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 199,
      description: 'For large-scale construction operations',
      features: [
        'Unlimited projects',
        'AI-powered insights',
        'White-label solution',
        '24/7 phone support',
        'Custom integrations',
        'Advanced security',
        'Dedicated account manager'
      ],
      color: 'success',
      popular: false
    }
  ];

  useEffect(() => {
    // Load current subscription status
    if (user?.id) {
      getSubscriptionStatus(user.id);
    }
  }, [user, getSubscriptionStatus]);

  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan);
    setPaymentDialogOpen(true);
  };

  const handlePaymentSuccess = (result) => {
    setPaymentDialogOpen(false);
    setSelectedPlan(null);
    // Refresh subscription status
    getSubscriptionStatus(user?.id);
  };

  const handleCancelSubscription = async () => {
    if (subscription?.id) {
      try {
        await cancelSubscription(subscription.id);
        getSubscriptionStatus(user?.id);
      } catch (error) {
        console.error('Failed to cancel subscription:', error);
      }
    }
  };

  const TabPanel = ({ children, value, index }) => (
    value === index ? <Box sx={{ pt: 3 }}>{children}</Box> : null
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom sx={{ textAlign: 'center' }}>
        Subscription Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
        Choose the perfect plan for your construction projects
      </Typography>

      {/* Current Subscription Status */}
      {subscription && (
        <Alert 
          severity="success" 
          icon={<CheckCircle />}
          sx={{ mb: 4 }}
        >
          <Typography variant="h6">
            Current Plan: {subscription.plan?.name || 'Active Subscription'}
          </Typography>
          <Typography variant="body2">
            Status: {subscription.status} • Next billing: {subscription.current_period_end}
          </Typography>
        </Alert>
      )}

      {/* Subscription Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
          <Tab label="Available Plans" />
          <Tab label="Billing History" />
          <Tab label="Payment Methods" />
        </Tabs>
      </Box>

      <TabPanel value={currentTab} index={0}>
        <Grid container spacing={3}>
          {plans.map((plan) => (
            <Grid item xs={12} md={4} key={plan.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  position: 'relative',
                  border: plan.popular ? '2px solid' : '1px solid',
                  borderColor: plan.popular ? 'primary.main' : 'grey.300',
                  boxShadow: plan.popular ? 4 : 1
                }}
              >
                {plan.popular && (
                  <Chip
                    label="Most Popular"
                    color="primary"
                    icon={<Star />}
                    sx={{
                      position: 'absolute',
                      top: -10,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      zIndex: 1
                    }}
                  />
                )}
                
                <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography variant="h5" fontWeight="bold" gutterBottom>
                      {plan.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {plan.description}
                    </Typography>
                    <Typography variant="h3" color={`${plan.color}.main`} fontWeight="bold">
                      ${plan.price}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      per month
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      Features included:
                    </Typography>
                    {plan.features.map((feature, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <CheckCircle sx={{ color: 'success.main', mr: 1, fontSize: 16 }} />
                        <Typography variant="body2">{feature}</Typography>
                      </Box>
                    ))}
                  </Box>

                  <Button
                    variant={plan.popular ? "contained" : "outlined"}
                    fullWidth
                    size="large"
                    sx={{ mt: 3, py: 1.5 }}
                    onClick={() => handlePlanSelect(plan)}
                    disabled={loading}
                  >
                    {subscription?.plan?.id === plan.id ? 'Current Plan' : 'Select Plan'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Billing History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your billing history will appear here once you have an active subscription.
            </Typography>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Payment Methods
              </Typography>
              <Button variant="outlined" startIcon={<Payment />}>
                Add Payment Method
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Manage your payment methods and billing information.
            </Typography>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Cancel Subscription */}
      {subscription && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Cancel />}
            onClick={handleCancelSubscription}
            disabled={loading}
          >
            Cancel Subscription
          </Button>
        </Box>
      )}

      {/* Payment Dialog */}
      <Dialog
        open={paymentDialogOpen}
        onClose={() => setPaymentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Subscribe to {selectedPlan?.name} Plan
        </DialogTitle>
        <DialogContent>
          {selectedPlan && (
            <PaymentForm
              priceId={selectedPlan.id}
              planName={selectedPlan.name}
              amount={`$${selectedPlan.price}`}
              onSuccess={handlePaymentSuccess}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SubscriptionManager;