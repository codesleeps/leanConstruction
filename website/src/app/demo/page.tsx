"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Building,
  Users,
  Building2,
  ArrowRight,
  CheckCircle,
  BarChart3,
  Zap,
  Shield,
  Eye
} from 'lucide-react';

const DemoPage = () => {
  const [selectedDemo, setSelectedDemo] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [demoCredentials, setDemoCredentials] = useState<any>(null);
  const router = useRouter();

  const demoTypes = [
    {
      id: 'small',
      name: 'Small Contractor',
      icon: Building,
      description: 'Perfect for small construction companies',
      employeeCount: '3-10 employees',
      projectCount: '3-10 projects',
      color: 'blue',
      features: [
        'Basic waste tracking',
        'Project management',
        'Simple analytics',
        'Team collaboration (up to 5 users)'
      ],
      sampleProjects: [
        'Residential Home Build - $250K',
        'Small Office Renovation - $75K'
      ]
    },
    {
      id: 'medium',
      name: 'Medium Builder',
      icon: Users,
      description: 'Ideal for growing construction businesses',
      employeeCount: '10-50 employees',
      projectCount: '10-50 projects',
      color: 'green',
      features: [
        'Advanced waste detection',
        'Team collaboration',
        'Detailed reporting',
        'AI-powered insights',
        'Mobile app access'
      ],
      sampleProjects: [
        'Commercial Building Phase 1 - $1.2M',
        'Shopping Center Development - $2.8M',
        'Industrial Warehouse - $850K'
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise Client',
      icon: Building2,
      description: 'Designed for large construction corporations',
      employeeCount: '50+ employees',
      projectCount: '50+ projects',
      color: 'purple',
      features: [
        'AI-powered predictions',
        'Custom integrations',
        'White-label options',
        'Advanced analytics',
        'Priority support',
        'Custom reporting'
      ],
      sampleProjects: [
        'Hospital Complex Construction - $15M',
        'Airport Terminal Expansion - $25M',
        'University Campus Development - $8M',
        'Skyscraper Project - $45M'
      ]
    }
  ];

  const handleCreateDemo = async (demoType: string) => {
    setIsCreating(true);
    setSelectedDemo(demoType);


    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/auth/demo-account/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          account_type: demoType
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create demo account');
      }

      setDemoCredentials(data);
    } catch (error) {
      console.error('Failed to create demo account:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const getColorClasses = (color: string) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: 'text-blue-600',
        button: 'bg-blue-600 hover:bg-blue-700',
        accent: 'text-blue-900'
      },
      green: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        icon: 'text-green-600',
        button: 'bg-green-600 hover:bg-green-700',
        accent: 'text-green-900'
      },
      purple: {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        icon: 'text-purple-600',
        button: 'bg-purple-600 hover:bg-purple-700',
        accent: 'text-purple-900'
      }
    };
    return colors[color as keyof typeof colors];
  };

  if (demoCredentials) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
        <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-3xl font-heading font-bold text-gray-900 mb-2">
              Demo Account Ready!
            </h2>
            <p className="text-gray-600">
              Your {demoTypes.find(d => d.id === selectedDemo)?.name} demo account has been created successfully.
            </p>
          </div>

          <div className="bg-gray-50 rounded-xl p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Demo Login Credentials</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <div className="mt-1 p-2 bg-white border rounded-lg font-mono text-sm">
                  {demoCredentials.demo_email}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <div className="mt-1 p-2 bg-white border rounded-lg font-mono text-sm">
                  {demoCredentials.demo_password}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <div className="flex items-start">
              <Eye className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
              <div>
                <h4 className="font-semibold text-blue-900">What You'll See</h4>
                <p className="text-blue-700 text-sm mt-1">
                  Explore realistic construction data including projects, waste logs, tasks, and AI-powered analytics.
                  All data is sample/demo data for illustration purposes.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => router.push('/login')}
              className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors flex items-center justify-center"
            >
              Login to Demo Account
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
            <button
              onClick={() => {
                setDemoCredentials(null);
                setSelectedDemo(null);
              }}
              className="flex-1 border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Try Different Demo
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <Link href="/" className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold mb-6">
            ← Back to Home
          </Link>
          <h1 className="text-4xl md:text-5xl font-heading font-bold text-gray-900 mb-4">
            Try Our Platform with Demo Data
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Explore Lean AI Construction with realistic sample data. No signup required -
            experience the power of AI-driven construction management instantly.
          </p>
        </div>

        {/* Demo Types */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {demoTypes.map((demo) => {
            const IconComponent = demo.icon;
            const colors = getColorClasses(demo.color);

            return (
              <div
                key={demo.id}
                className={`bg-white rounded-2xl shadow-lg border-2 ${colors.border} overflow-hidden hover:shadow-xl transition-shadow duration-300`}
              >
                <div className={`${colors.bg} p-6 text-center`}>
                  <div className={`w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <IconComponent className={`w-8 h-8 ${colors.icon}`} />
                  </div>
                  <h3 className={`text-xl font-heading font-bold ${colors.accent} mb-2`}>
                    {demo.name}
                  </h3>
                  <p className="text-gray-600 text-sm">{demo.description}</p>
                </div>

                <div className="p-6">
                  <div className="space-y-4 mb-6">
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="w-4 h-4 mr-2" />
                      {demo.employeeCount}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Building className="w-4 h-4 mr-2" />
                      {demo.projectCount}
                    </div>
                  </div>

                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-900 mb-3">Features Included:</h4>
                    <ul className="space-y-2">
                      {demo.features.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-900 mb-3">Sample Projects:</h4>
                    <ul className="space-y-2">
                      {demo.sampleProjects.slice(0, 2).map((project, index) => (
                        <li key={index} className="text-sm text-gray-600">
                          • {project}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <button
                    onClick={() => handleCreateDemo(demo.id)}
                    disabled={isCreating && selectedDemo === demo.id}
                    className={`w-full ${colors.button} text-white py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center`}
                  >
                    {isCreating && selectedDemo === demo.id ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    ) : (
                      <Eye className="w-5 h-5 mr-2" />
                    )}
                    Try {demo.name} Demo
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Feature Highlights */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-heading font-bold text-gray-900 text-center mb-8">
            What You'll Experience
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Analytics</h3>
              <p className="text-gray-600">
                Track waste reduction, project progress, and cost savings with interactive dashboards and reports.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
              <p className="text-gray-600">
                Discover hidden patterns and get predictive analytics to prevent delays and optimize workflows.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Enterprise Security</h3>
              <p className="text-gray-600">
                Bank-level encryption and compliance with industry standards keep your data safe and secure.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoPage;