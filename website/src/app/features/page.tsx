import Link from "next/link";
import {
  ArrowRight,
  Camera,
  Brain,
  BarChart3,
  Zap,
  Users,
  Shield,
  Workflow,
  LineChart,
  Bell,
  FileText,
  Globe,
  Smartphone,
  Cloud,
  Lock,
  RefreshCw,
  CheckCircle,
} from "lucide-react";

const mainFeatures = [
  {
    id: "waste-detection",
    name: "AI-Powered Waste Detection",
    description:
      "Our computer vision technology analyzes images and video feeds from your construction sites to identify waste in real-time. From material overuse to inefficient processes, our AI spots opportunities for improvement that humans might miss.",
    icon: Camera,
    color: "bg-blue-500",
    benefits: [
      "Reduce material waste by up to 30%",
      "Real-time alerts for waste events",
      "Automatic categorization of waste types",
      "Historical trend analysis",
      "Integration with site cameras",
    ],
    image: "/features/waste-detection.png",
  },
  {
    id: "predictive-analytics",
    name: "Predictive Analytics",
    description:
      "Machine learning models trained on millions of construction data points help you forecast project outcomes before they happen. Anticipate delays, budget overruns, and resource shortages weeks in advance.",
    icon: Brain,
    color: "bg-purple-500",
    benefits: [
      "Predict delays 2-4 weeks in advance",
      "Budget forecasting with 95% accuracy",
      "Resource optimization recommendations",
      "Risk scoring for project phases",
      "What-if scenario modeling",
    ],
    image: "/features/predictive-analytics.png",
  },
  {
    id: "dashboards",
    name: "Real-Time Dashboards",
    description:
      "Monitor all your projects from a single, customizable dashboard. Get live updates on KPIs, project status, team performance, and more. Share dashboards with stakeholders for complete transparency.",
    icon: BarChart3,
    color: "bg-green-500",
    benefits: [
      "Customizable widgets and layouts",
      "Real-time data synchronization",
      "Multi-project overview",
      "Exportable reports",
      "Stakeholder sharing",
    ],
    image: "/features/dashboards.png",
  },
  {
    id: "lean-tools",
    name: "Lean Methodology Tools",
    description:
      "Built-in tools for implementing lean construction principles. From 5S audits to Kanban boards and value stream mapping, everything you need to optimize your workflows is at your fingertips.",
    icon: Zap,
    color: "bg-yellow-500",
    benefits: [
      "Digital 5S audit checklists",
      "Kanban boards for task management",
      "Value stream mapping tools",
      "Continuous improvement tracking",
      "Lean metrics and KPIs",
    ],
    image: "/features/lean-tools.png",
  },
  {
    id: "collaboration",
    name: "Team Collaboration",
    description:
      "Keep your entire team aligned with shared workspaces, task management, and real-time communication. From field workers to executives, everyone stays informed and connected.",
    icon: Users,
    color: "bg-pink-500",
    benefits: [
      "Shared project workspaces",
      "Task assignment and tracking",
      "In-app messaging and comments",
      "File sharing and versioning",
      "Mobile app for field teams",
    ],
    image: "/features/collaboration.png",
  },
  {
    id: "security",
    name: "Enterprise Security",
    description:
      "Your data is protected with bank-level encryption, SSO integration, and compliance with industry standards. We take security seriously so you can focus on building.",
    icon: Shield,
    color: "bg-red-500",
    benefits: [
      "256-bit AES encryption",
      "SSO/SAML integration",
      "SOC 2 Type II certified",
      "GDPR compliant",
      "Role-based access control",
    ],
    image: "/features/security.png",
  },
];

const additionalFeatures = [
  {
    name: "Workflow Automation",
    description:
      "Automate repetitive tasks and approvals with customizable workflows.",
    icon: Workflow,
  },
  {
    name: "Advanced Reporting",
    description:
      "Generate detailed reports with custom metrics and visualizations.",
    icon: LineChart,
  },
  {
    name: "Smart Notifications",
    description:
      "Get alerted about important events via email, SMS, or push notifications.",
    icon: Bell,
  },
  {
    name: "Document Management",
    description:
      "Store, organize, and version control all your project documents.",
    icon: FileText,
  },
  {
    name: "Multi-Language Support",
    description: "Available in 12 languages for global construction teams.",
    icon: Globe,
  },
  {
    name: "Mobile Apps",
    description: "Native iOS and Android apps for on-site access.",
    icon: Smartphone,
  },
  {
    name: "Cloud Infrastructure",
    description: "99.9% uptime SLA with global CDN for fast access anywhere.",
    icon: Cloud,
  },
  {
    name: "API Access",
    description: "RESTful API for custom integrations and data access.",
    icon: Lock,
  },
  {
    name: "Data Sync",
    description: "Real-time sync across all devices and team members.",
    icon: RefreshCw,
  },
];

const integrations = [
  { name: "Procore", logo: "/integrated_tools_logo/procore.webp" },
  { name: "Autodesk", logo: "/integrated_tools_logo/autodesk.webp" },
  {
    name: "Microsoft Project",
    logo: "/integrated_tools_logo/microsoft-project.webp",
  },
  { name: "Primavera P6", logo: "/integrated_tools_logo/Primavera-P6.webp" },
  { name: "Bluebeam", logo: "/integrated_tools_logo/Bluebeam.webp" },
  { name: "PlanGrid", logo: "/integrated_tools_logo/plangrid-logo.webp" },
  { name: "Sage", logo: "/integrated_tools_logo/sage.webp" },
  { name: "QuickBooks", logo: "/integrated_tools_logo/intuit-quickbooks.webp" },
];

export default function FeaturesPage() {
  return (
    <div className="overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 gradient-bg overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />
        </div>

        <div className="container-custom relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold text-white">
              Powerful Features for{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                Modern Construction
              </span>
            </h1>
            <p className="mt-6 text-lg md:text-xl text-white/80">
              Everything you need to manage construction projects efficiently,
              reduce waste, and deliver on time and under budget.
            </p>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg
            viewBox="0 0 1440 120"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
              fill="#F9FAFB"
            />
          </svg>
        </div>
      </section>

      {/* Main Features */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          {mainFeatures.map((feature, index) => (
            <div
              key={feature.id}
              id={feature.id}
              className={`flex flex-col ${
                index % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"
              } gap-12 items-center ${
                index > 0 ? "mt-24" : ""
              } max-w-7xl mx-auto`}
            >
              {/* Content */}
              <div className="flex-1">
                <div
                  className={`w-14 h-14 rounded-2xl ${feature.color} flex items-center justify-center mb-6`}
                >
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
                  {feature.name}
                </h2>
                <p className="mt-4 text-lg text-gray-600">
                  {feature.description}
                </p>
                <ul className="mt-8 space-y-4">
                  {feature.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Image Placeholder */}
              <div className="flex-1">
                <div className="relative">
                  <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl shadow-xl overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div
                        className={`w-24 h-24 rounded-3xl ${feature.color} opacity-20`}
                      />
                      <feature.icon className="absolute w-12 h-12 text-gray-400" />
                    </div>
                  </div>
                  {/* Decorative elements */}
                  <div
                    className={`absolute -z-10 -top-4 -right-4 w-full h-full rounded-2xl ${feature.color} opacity-10`}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Additional Features Grid */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              And so much <span className="gradient-text">more</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Discover all the tools and features that make Lean AI Construction
              the most comprehensive platform for modern construction
              management.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {additionalFeatures.map((feature) => (
              <div
                key={feature.name}
                className="flex gap-4 p-6 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-heading font-semibold text-gray-900">
                    {feature.name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section id="integrations" className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Integrates with your{" "}
              <span className="gradient-text">favorite tools</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Connect Lean AI Construction with the tools you already use. Our
              platform integrates seamlessly with industry-leading software.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {integrations.map((integration) => (
              <div
                key={integration.name}
                className="flex items-center justify-center p-8 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto bg-gray-100 rounded-xl flex items-center justify-center mb-3">
                    <span className="text-2xl font-bold text-gray-400">
                      {integration.name.charAt(0)}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {integration.name}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600 mb-4">
              Don't see your tool? We're always adding new integrations.
            </p>
            <Link
              href="/contact"
              className="text-primary-600 font-semibold hover:text-primary-700"
            >
              Request an integration →
            </Link>
          </div>
        </div>
      </section>

      {/* API Section */}
      <section id="api" className="section-padding bg-gray-900">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-heading font-bold text-white">
                Build custom solutions with our{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                  powerful API
                </span>
              </h2>
              <p className="mt-4 text-lg text-gray-400">
                Our RESTful API gives you full access to your data and platform
                capabilities. Build custom integrations, automate workflows, and
                extend functionality to meet your unique needs.
              </p>
              <ul className="mt-8 space-y-4">
                {[
                  "RESTful API with comprehensive documentation",
                  "Webhooks for real-time event notifications",
                  "OAuth 2.0 authentication",
                  "Rate limiting and usage analytics",
                  "Sandbox environment for testing",
                ].map((item) => (
                  <li
                    key={item}
                    className="flex items-center gap-3 text-gray-300"
                  >
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    {item}
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link href="/docs" className="btn-primary">
                  View API Documentation
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>

            {/* Code Preview */}
            <div className="bg-gray-800 rounded-2xl p-6 font-mono text-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <pre className="text-gray-300 overflow-x-auto">
                {`// Get project analytics
const response = await fetch(
  'https://api.leanaiconstruction.com/v1/projects/123/analytics',
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    }
  }
);

const data = await response.json();
console.log(data);

// Response
{
  "project_id": "123",
  "waste_reduction": "32%",
  "cost_savings": "$2.4M",
  "schedule_variance": "-3 days",
  "predictions": {
    "completion_date": "2024-06-15",
    "confidence": 0.94
  }
}`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="relative overflow-hidden rounded-3xl gradient-bg p-12 md:p-20">
            <div className="absolute inset-0 opacity-10">
              <div
                className="absolute inset-0"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                }}
              />
            </div>

            <div className="relative z-10 text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-white">
                Ready to see these features in action?
              </h2>
              <p className="mt-6 text-lg md:text-xl text-white/80">
                Start your free trial today and experience the power of
                AI-driven construction management.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/signup"
                  className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg px-8 py-4"
                >
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link
                  href="/contact"
                  className="btn-secondary border-white/30 text-white hover:bg-white/10 text-lg px-8 py-4"
                >
                  Schedule a Demo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
