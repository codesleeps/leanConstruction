"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  CheckCircle,
  Circle,
  ArrowRight,
  User,
  FolderPlus,
  BarChart3,
  Zap,
  Mail,
  Phone,
  Building,
  Users
} from 'lucide-react';

interface OnboardingProgress {
  current_step: number;
  completed_steps: number[];
  profile_completed: boolean;
  first_project_created: boolean;
  features_explored: string[];
}

const OnboardingDashboard = () => {
  const [progress, setProgress] = useState<OnboardingProgress | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    fetchOnboardingProgress();
  }, []);

  const fetchOnboardingProgress = async () => {

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/v1/onboarding/progress`);
      if (response.ok) {
        const data = await response.json();
        setProgress(data);
        setCurrentStep(data.current_step);
      }
    } catch (error) {
      console.error('Failed to fetch onboarding progress:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const completeStep = async (stepType: string, stepData?: any) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${API_URL}/api/v1/onboarding/track-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: stepType,
          event_data: stepData || {}
        }),
      });

      // Refresh progress
      fetchOnboardingProgress();
    } catch (error) {
      console.error('Failed to track event:', error);
    }
  };

  const onboardingSteps = [
    {
      id: 0,
      title: "Account Created",
      description: "Welcome to Lean AI Construction!",
      icon: CheckCircle,
      status: "completed",
      action: null
    },
    {
      id: 1,
      title: "Verify Email",
      description: "Check your inbox and verify your email address",
      icon: Mail,
      status: progress?.completed_steps.includes(1) ? "completed" : "current",
      action: {
        text: "Resend Verification",
        onClick: () => console.log("Resend verification email")
      }
    },
    {
      id: 2,
      title: "Complete Profile",
      description: "Tell us about your company and projects",
      icon: User,
      status: progress?.completed_steps.includes(2) ? "completed" : "pending",
      action: {
        text: "Complete Profile",
        onClick: () => completeStep("profile_completed", { completed_at: new Date().toISOString() })
      }
    },
    {
      id: 3,
      title: "Create First Project",
      description: "Set up your first construction project",
      icon: FolderPlus,
      status: progress?.completed_steps.includes(3) ? "completed" : "pending",
      action: {
        text: "Create Project",
        onClick: () => console.log("Navigate to project creation")
      }
    },
    {
      id: 4,
      title: "Explore Features",
      description: "Discover AI-powered waste detection and analytics",
      icon: Zap,
      status: progress?.completed_steps.includes(4) ? "completed" : "pending",
      action: {
        text: "Explore Features",
        onClick: () => completeStep("feature_explored", { feature_name: "dashboard_overview" })
      }
    },
    {
      id: 5,
      title: "Onboarding Complete",
      description: "You're all set! Start building smarter",
      icon: BarChart3,
      status: progress?.completed_steps.includes(5) ? "completed" : "pending",
      action: {
        text: "Go to Dashboard",
        onClick: () => window.location.href = "/dashboard"
      }
    }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-heading font-bold text-gray-900">
              Welcome to Lean AI Construction
            </h1>
            <Link
              href="/dashboard"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Skip Onboarding
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Overview */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Your Onboarding Progress</h2>
              <p className="text-gray-600 mt-1">
                {progress?.completed_steps.length || 0} of {onboardingSteps.length} steps completed
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-primary-600">
                {Math.round(((progress?.completed_steps.length || 0) / onboardingSteps.length) * 100)}%
              </div>
              <div className="text-sm text-gray-500">Complete</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${((progress?.completed_steps.length || 0) / onboardingSteps.length) * 100}%`
              }}
            ></div>
          </div>
        </div>

        {/* Onboarding Steps */}
        <div className="space-y-6">
          {onboardingSteps.map((step, index) => {
            const IconComponent = step.icon;
            const isCompleted = step.status === "completed";
            const isCurrent = step.status === "current";

            return (
              <div
                key={step.id}
                className={`bg-white rounded-xl shadow-sm border-2 transition-all duration-200 ${isCompleted ? 'border-green-200 bg-green-50' :
                  isCurrent ? 'border-primary-200 bg-primary-50' :
                    'border-gray-200'
                  }`}
              >
                <div className="p-6">
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${isCompleted ? 'bg-green-100' :
                      isCurrent ? 'bg-primary-100' :
                        'bg-gray-100'
                      }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : (
                        <IconComponent className={`w-6 h-6 ${isCurrent ? 'text-primary-600' : 'text-gray-400'
                          }`} />
                      )}
                    </div>

                    <div className="ml-4 flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className={`text-lg font-semibold ${isCompleted ? 'text-green-900' :
                            isCurrent ? 'text-primary-900' :
                              'text-gray-900'
                            }`}>
                            {step.title}
                          </h3>
                          <p className={`text-sm mt-1 ${isCompleted ? 'text-green-700' :
                            isCurrent ? 'text-primary-700' :
                              'text-gray-600'
                            }`}>
                            {step.description}
                          </p>
                        </div>

                        {step.action && (
                          <button
                            onClick={step.action.onClick}
                            className={`ml-4 px-4 py-2 rounded-lg font-medium transition-colors ${isCompleted ? 'bg-green-100 text-green-700 cursor-not-allowed' :
                              'bg-primary-600 text-white hover:bg-primary-700'
                              }`}
                            disabled={isCompleted}
                          >
                            {step.action.text}
                          </button>
                        )}
                      </div>

                      {isCurrent && (
                        <div className="mt-4 p-4 bg-primary-100 rounded-lg">
                          <div className="flex items-center text-primary-800">
                            <Circle className="w-4 h-4 mr-2 fill-current" />
                            <span className="text-sm font-medium">Current Step</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl p-6 text-white">
          <h3 className="text-xl font-semibold mb-2">Need Help Getting Started?</h3>
          <p className="text-primary-100 mb-4">
            Our team is here to help you make the most of Lean AI Construction.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              href="/help"
              className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              View Help Center
            </Link>
            <Link
              href="/contact"
              className="border border-white text-white px-4 py-2 rounded-lg font-medium hover:bg-white hover:text-primary-600 transition-colors"
            >
              Contact Support
            </Link>
          </div>
        </div>

        {/* Demo Data Preview */}
        <div className="mt-8 bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">See What You'll Get</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Real-time Analytics</h4>
              <p className="text-sm text-gray-600">
                Track waste reduction, project progress, and cost savings in real-time
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">AI Predictions</h4>
              <p className="text-sm text-gray-600">
                Get AI-powered insights to prevent delays and optimize workflows
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Team Collaboration</h4>
              <p className="text-sm text-gray-600">
                Keep your entire team aligned with shared workspaces and updates
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingDashboard;