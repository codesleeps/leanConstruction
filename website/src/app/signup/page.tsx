"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, CheckCircle, Building2, Users, Building } from 'lucide-react';

const signup = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    company: '',
    role: '',
    companySize: '',
    constructionType: '',
    phoneNumber: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/onboarding/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Redirect to verification page
      router.push('/verify-email?email=' + encodeURIComponent(formData.email));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold">
            ← Back to Home
          </Link>
          <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900">
            Start Your Construction AI Journey
          </h2>
          <p className="mt-2 text-lg text-gray-600">
            Join 500+ construction teams already building smarter
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className="flex items-center text-primary-600">
            <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
              1
            </div>
            <span className="ml-2 font-medium">Sign Up</span>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="flex items-center text-gray-400">
            <div className="w-8 h-8 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-sm font-semibold">
              2
            </div>
            <span className="ml-2">Verify Email</span>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
          <div className="flex items-center text-gray-400">
            <div className="w-8 h-8 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-sm font-semibold">
              3
            </div>
            <span className="ml-2">Get Started</span>
          </div>
        </div>

        {/* Demo Account Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">🚀 Try Demo Account</h3>
          <p className="text-blue-700 mb-4">
            Explore our platform with sample data before committing to registration.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="flex items-center mb-2">
                <Building className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-semibold text-blue-900">Small Contractor</span>
              </div>
              <p className="text-sm text-blue-700">3-10 projects</p>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="flex items-center mb-2">
                <Users className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-semibold text-blue-900">Medium Builder</span>
              </div>
              <p className="text-sm text-blue-700">10-50 projects</p>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="flex items-center mb-2">
                <Building2 className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-semibold text-blue-900">Enterprise</span>
              </div>
              <p className="text-sm text-blue-700">50+ projects</p>
            </div>
          </div>
          <button className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
            Try Demo Account
          </button>
        </div>

        {/* Registration Form */}
        <form className="bg-white rounded-xl shadow-lg p-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Personal Information */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                required
                value={formData.fullName}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="John Smith"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="john@company.com"
              />
            </div>

            <div>
              <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                id="phoneNumber"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Company Information */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                Company Name *
              </label>
              <input
                type="text"
                id="company"
                name="company"
                required
                value={formData.company}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="ABC Construction"
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                Your Role *
              </label>
              <select
                id="role"
                name="role"
                required
                value={formData.role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Select your role</option>
                <option value="owner">Owner</option>
                <option value="project_manager">Project Manager</option>
                <option value="site_supervisor">Site Supervisor</option>
                <option value="foreman">Foreman</option>
                <option value="estimator">Estimator</option>
                <option value="engineer">Engineer</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="companySize" className="block text-sm font-medium text-gray-700 mb-2">
                Company Size *
              </label>
              <select
                id="companySize"
                name="companySize"
                required
                value={formData.companySize}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Select company size</option>
                <option value="small">Small (3-10 employees)</option>
                <option value="medium">Medium (10-50 employees)</option>
                <option value="enterprise">Enterprise (50+ employees)</option>
              </select>
            </div>

            <div>
              <label htmlFor="constructionType" className="block text-sm font-medium text-gray-700 mb-2">
                Construction Type *
              </label>
              <select
                id="constructionType"
                name="constructionType"
                required
                value={formData.constructionType}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Select construction type</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="industrial">Industrial</option>
              </select>
            </div>
          </div>

          {/* Terms and Privacy */}
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                required
                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <label htmlFor="terms" className="text-gray-700">
                I agree to the{' '}
                <Link href="/terms" className="text-primary-600 hover:text-primary-500">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-primary-600 hover:text-primary-500">
                  Privacy Policy
                </Link>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Creating Account...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                Create Account
                <ArrowRight className="ml-2 h-5 w-5" />
              </div>
            )}
          </button>

          <div className="text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link href="/login" className="text-primary-600 hover:text-primary-500 font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default signup;