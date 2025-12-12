"use client";

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle, XCircle, Mail, Loader } from 'lucide-react';

const VerifyEmail = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setStatus('error');
      setMessage('No verification token provided');
      return;
    }

    verifyEmail(token);
  }, [searchParams]);

  const verifyEmail = async (token: string) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Verification failed');
      }

      setStatus('success');
      setMessage(data.message || 'Email verified successfully!');
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Verification failed');
    }
  };

  const handleContinueToLogin = () => {
    router.push('/login');
  };

  const handleContinueToDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold">
            ← Back to Home
          </Link>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          {status === 'loading' && (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-6">
                <Loader className="h-8 w-8 text-blue-600 animate-spin" />
              </div>
              <h2 className="text-2xl font-heading font-bold text-gray-900 mb-4">
                Verifying Your Email
              </h2>
              <p className="text-gray-600">
                Please wait while we verify your email address...
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-heading font-bold text-gray-900 mb-4">
                Email Verified Successfully! 🎉
              </h2>
              <p className="text-gray-600 mb-6">
                {message}
              </p>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-2">
                  <Mail className="w-5 h-5 text-green-600 mr-2" />
                  <span className="font-semibold text-green-900">You're all set!</span>
                </div>
                <p className="text-sm text-green-700">
                  Your account is now active. You can access all features of Lean AI Construction.
                </p>
              </div>

              <div className="space-y-4">
                <button
                  onClick={handleContinueToDashboard}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                >
                  Go to Dashboard
                </button>

                <button
                  onClick={handleContinueToLogin}
                  className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
                >
                  Sign In Instead
                </button>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
              <h2 className="text-2xl font-heading font-bold text-gray-900 mb-4">
                Verification Failed
              </h2>
              <p className="text-gray-600 mb-6">
                {message}
              </p>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-red-900 mb-2">Common Issues:</h3>
                <ul className="text-sm text-red-700 space-y-1 text-left">
                  <li>• The verification link has expired (24 hours)</li>
                  <li>• The link has already been used</li>
                  <li>• There was an error in the verification process</li>
                </ul>
              </div>

              <div className="space-y-4">
                <Link
                  href="/signup"
                  className="block w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 text-center focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                >
                  Register Again
                </Link>

                <Link
                  href="/login"
                  className="block w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-200 text-center focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
                >
                  Sign In
                </Link>
              </div>
            </>
          )}
        </div>

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
};

export default VerifyEmail;