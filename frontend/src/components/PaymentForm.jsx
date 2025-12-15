import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import {
  useStripe,
  useElements,
  PaymentElement,
  AddressElement
} from '@stripe/react-stripe-js';
import { CheckCircle, CreditCard, Security } from '@mui/icons-material';
import { useStripePayment } from './StripePaymentContext';

const PaymentForm = ({ priceId, planName, amount, onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const {
    clientSecret,
    loading,
    error,
    confirmPayment,
    setError
  } = useStripePayment();
  
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setSubmitting(true);
    setMessage('');
    setError(null);

    try {
      // Confirm the payment with Stripe
      const { error: submitError } = await elements.submit();
      if (submitError) {
        setError(submitError.message);
        setSubmitting(false);
        return;
      }

      // Create payment method
      const { error: pmError, paymentMethod } = await stripe.createPaymentMethod({
        elements,
      });

      if (pmError) {
        setError(pmError.message);
        setSubmitting(false);
        return;
      }

      // Confirm the subscription
      const result = await confirmPayment(paymentMethod.id, 'demo-customer-id');
      
      if (result.success) {
        setMessage('Subscription created successfully!');
        if (onSuccess) {
          onSuccess(result);
        }
      } else {
        setError(result.error || 'Failed to create subscription');
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  if (!clientSecret) {
    return (
      <Alert severity="info">
        Initializing payment form...
      </Alert>
    );
  }

  return (
    <Card sx={{ maxWidth: 500, mx: 'auto', mt: 3 }}>
      <CardContent sx={{ p: 4 }}>
        {/* Plan Summary */}
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            {planName}
          </Typography>
          <Typography variant="h3" color="primary" fontWeight="bold">
            {amount}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            per month
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Payment Form */}
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <CreditCard sx={{ mr: 1 }} />
              Payment Information
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <PaymentElement 
                options={{
                  layout: 'tabs'
                }}
              />
            </Box>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Billing Address
              </Typography>
              <AddressElement options={{ mode: 'billing' }} />
            </Box>
          </Box>

          {/* Security Notice */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            bgcolor: 'grey.50', 
            p: 2, 
            borderRadius: 1, 
            mb: 3 
          }}>
            <Security sx={{ color: 'success.main', mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              Your payment information is secure and encrypted
            </Typography>
          </Box>

          {/* Error Message */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Success Message */}
          {message && (
            <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
              {message}
            </Alert>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={!stripe || submitting || loading}
            sx={{
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
              }
            }}
          >
            {submitting || loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
                Processing...
              </Box>
            ) : (
              `Subscribe to ${planName}`
            )}
          </Button>
        </form>

        {/* Features List */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Plan Features:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {[
              'Advanced Analytics',
              'Waste Detection',
              'Priority Support',
              'API Access',
              'Custom Reports'
            ].map((feature, index) => (
              <Chip 
                key={index}
                label={feature}
                size="small"
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PaymentForm;