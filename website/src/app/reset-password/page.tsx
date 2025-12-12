"use client";

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle, XCircle, Lock, Loader, Eye, EyeOff } from 'lucide-react';

export const dynamic = 'force-dynamic';

function ResetPasswordForm() {
  const [status, setStatus] = useState<'request' | 'reset' | 'loading' | 'success' | 'error'>('request');
  const [previousStatus, setPreviousStatus] = useState<'request' | 'reset'>('request');
  const [message, setMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const [requestForm, setRequestForm] = useState({
    email: ''
  });

  const [resetForm, setResetForm] = useState({
    password: '',
    confirmPassword: ''
  });

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      setStatus('reset');
    }
  }, [searchParams]);

  const handleRequestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: requestForm.email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }

      setPreviousStatus('request');
      setStatus('success');
      setMessage(data.message);
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Request failed');
    }
  };

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (resetForm.password !== resetForm.confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }

    if (resetForm.password.length < 8) {
      setMessage('Password must be at least 8 characters long');
      return;
    }

    setStatus('loading');

    try {
      const token = searchParams.get('token');

      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: resetForm.password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Reset failed');
      }

      setPreviousStatus('reset');
      setStatus('success');
      setMessage(data.message);
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Reset failed');
    }
  };

  const handleLogin = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold">
            ← Back to Home
          </Link>
          <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900">
            {status === 'request' && 'Reset Your Password'}
            {status === 'reset' && 'Set New Password'}
            {status === 'loading' && 'Processing...'}
            {status === 'success' && 'Password Reset Complete'}
            {status === 'error' && 'Reset Failed'}
          </h2>
        </div>

        {/* Request Reset Form */}
        {status === 'request' && (
          <form className="bg-white rounded-xl shadow-lg p-8 space-y-6" onSubmit={handleRequestSubmit}>
            <div className="text-center mb-6">
              <Lock className="mx-auto h-12 w-12 text-primary-600" />
              <p className="mt-2 text-gray-600">
                Enter your email address and we'll send you a link to reset your password.
              </p>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                required
                value={requestForm.email}
                onChange={(e) => setRequestForm({ ...requestForm, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="john@company.com"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              Send Reset Link
            </button>

            <div className="text-center">
              <p className="text-gray-600">
                Remember your password?{' '}
                <Link href="/login" className="text-primary-600 hover:text-primary-500 font-semibold">
                  Sign in
                </Link>
              </p>
            </div>
          </form>
        )}

        {/* Reset Password Form */}
        {status === 'reset' && (
          <form className="bg-white rounded-xl shadow-lg p-8 space-y-6" onSubmit={handleResetSubmit}>
            <div className="text-center mb-6">
              <Lock className="mx-auto h-12 w-12 text-primary-600" />
              <p className="mt-2 text-gray-600">
                Enter your new password below.
              </p>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  required
                  value={resetForm.password}
                  onChange={(e) => setResetForm({ ...resetForm, password: e.target.value })}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  required
                  value={resetForm.confirmPassword}
                  onChange={(e) => setResetForm({ ...resetForm, confirmPassword: e.target.value })}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              Reset Password
            </button>
          </form>
        )}

        {/* Loading State */}
        {status === 'loading' && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-6">
              <Loader className="h-8 w-8 text-blue-600 animate-spin" />
            </div>
            <p className="text-gray-600">
              Processing your request...
            </p>
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-heading font-bold text-gray-900 mb-4">
              {previousStatus === 'request' ? 'Check Your Email' : 'Password Reset Successful!'}
            </h3>
            <p className="text-gray-600 mb-6">
              {message}
            </p>

            {previousStatus === 'request' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-700">
                  We've sent password reset instructions to your email address.
                  Please check your inbox and follow the link to reset your password.
                </p>
              </div>
            )}

            <button
              onClick={handleLogin}
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              Continue to Sign In
            </button>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
            <h3 className="text-xl font-heading font-bold text-gray-900 mb-4">
              Reset Failed
            </h3>
            <p className="text-gray-600 mb-6">
              {message}
            </p>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-red-900 mb-2">Common Issues:</h4>
              <ul className="text-sm text-red-700 space-y-1 text-left">
                <li>• The reset link has expired (1 hour)</li>
                <li>• The link has already been used</li>
                <li>• There was an error processing your request</li>
              </ul>
            </div>

            <div className="space-y-4">
              <Link
                href="/reset-password"
                className="block w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 text-center focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
              >
                Try Again
              </Link>

              <Link
                href="/login"
                className="block w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-200 text-center focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Need help?{' '}
            <Link href="/contact" className="text-primary-600 hover:text-primary-500 font-semibold">
              Contact Support
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function ResetPassword() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 text-primary-600 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}