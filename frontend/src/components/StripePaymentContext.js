import React, { createContext, useContext, useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import axios from 'axios';

// Initialize Stripe (in production, use environment variables)
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || 'pk_test_51234567890abcdef');

const StripePaymentContext = createContext();

export const useStripePayment = () => {
  const context = useContext(StripePaymentContext);
  if (!context) {
    throw new Error('useStripePayment must be used within a StripePaymentProvider');
  }
  return context;
};

export const StripePaymentProvider = ({ children }) => {
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [subscription, setSubscription] = useState(null);

  // Initialize payment intent for subscription
  const createSubscription = async (priceId, customerId = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}/api/v1/payments/create-subscription`, {
        price_id: priceId,
        customer_id: customerId
      });
      
      setClientSecret(response.data.client_secret);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create subscription');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Confirm payment
  const confirmPayment = async (paymentMethodId, customerId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}/api/v1/payments/confirm-subscription`, {
        payment_method_id: paymentMethodId,
        customer_id: customerId,
        client_secret: clientSecret
      });
      
      setSubscription(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to confirm payment');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Cancel subscription
  const cancelSubscription = async (subscriptionId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}/api/v1/payments/cancel-subscription`, {
        subscription_id: subscriptionId
      });
      
      setSubscription(null);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel subscription');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get current subscription status
  const getSubscriptionStatus = async (customerId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}/api/v1/payments/subscription-status/${customerId}`);
      setSubscription(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to get subscription status:', err);
      return null;
    }
  };

  const value = {
    clientSecret,
    loading,
    error,
    subscription,
    createSubscription,
    confirmPayment,
    cancelSubscription,
    getSubscriptionStatus,
    setError,
    stripePromise
  };

  return (
    <StripePaymentContext.Provider value={value}>
      <Elements stripe={stripePromise}>
        {children}
      </Elements>
    </StripePaymentContext.Provider>
  );
};