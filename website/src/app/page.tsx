import Link from "next/link";
import Image from "next/image";
import {
  ArrowRight,
  CheckCircle,
  BarChart3,
  Brain,
  Camera,
  Shield,
  Zap,
  Users,
  TrendingUp,
  Clock,
  DollarSign,
  Leaf,
  Star
} from "lucide-react";

const features = [
  {
    name: "AI-Powered Waste Detection",
    description: "Computer vision technology identifies waste in real-time, helping you reduce material costs by up to 30%.",
    icon: Camera,
    color: "bg-blue-500",
  },
  {
    name: "Predictive Analytics",
    description: "Machine learning models forecast project delays, budget overruns, and resource needs before they happen.",
    icon: Brain,
    color: "bg-purple-500",
  },
  {
    name: "Real-Time Dashboards",
    description: "Monitor all your projects from a single dashboard with live updates and customizable KPIs.",
    icon: BarChart3,
    color: "bg-green-500",
  },
  {
    name: "Site Progress Monitoring",
    description: "Computer vision tracks construction progress automatically, providing accurate status updates and milestone tracking.",
    icon: TrendingUp,
    color: "bg-indigo-500",
  },
  {
    name: "Safety Compliance Detection",
    description: "AI-powered safety monitoring detects compliance violations and safety hazards in real-time to prevent accidents.",
    icon: Shield,
    color: "bg-red-500",
  },
  {
    name: "Equipment Tracking",
    description: "Computer vision automatically tracks equipment location, usage, and maintenance needs across your job sites.",
    icon: Zap,
    color: "bg-orange-500",
  },
  {
    name: "5S Assessment",
    description: "AI-driven 5S methodology evaluation ensures workplace organization and standardization across all projects.",
    icon: CheckCircle,
    color: "bg-teal-500",
  },
  {
    name: "Lean Methodology Tools",
    description: "Built-in 5S, Kanban, and value stream mapping tools to optimize your construction workflows.",
    icon: Users,
    color: "bg-yellow-500",
  },
  {
    name: "Team Collaboration",
    description: "Keep your entire team aligned with shared workspaces, task management, and real-time communication.",
    icon: Users,
    color: "bg-pink-500",
  },
];

const stats = [
  { value: "30%", label: "Cost Reduction", icon: DollarSign },
  { value: "45%", label: "Less Waste", icon: Leaf },
  { value: "2x", label: "Faster Delivery", icon: Clock },
  { value: "98%", label: "Client Satisfaction", icon: TrendingUp },
];

const testimonials = [
  {
    content: "Lean AI Construction transformed how we manage our projects. We've seen a 35% reduction in material waste and our project timelines have improved dramatically.",
    author: "Sarah Johnson",
    role: "Project Director",
    company: "BuildRight Construction",
    rating: 5,
  },
  {
    content: "The predictive analytics feature alone has saved us millions. We can now anticipate issues before they become costly problems.",
    author: "Michael Chen",
    role: "CEO",
    company: "Pacific Builders",
    rating: 5,
  },
  {
    content: "Finally, a construction management platform that understands lean principles. The waste detection AI is incredibly accurate.",
    author: "Emma Williams",
    role: "Operations Manager",
    company: "GreenBuild Solutions",
    rating: 5,
  },
];

const trustedBy = [
  {
    name: "Aecom",
    logo: "/trustedByLeadingCompanies/Aecom-logo.webp",
    alt: "Aecom Logo"
  },
  {
    name: "BlackRidge",
    logo: "/trustedByLeadingCompanies/BLACKRIDGE+1-528w.webp",
    alt: "BlackRidge Logo"
  },
  {
    name: "Hensel Phelps",
    logo: "/trustedByLeadingCompanies/Hensel_Phelps_200_200.webp",
    alt: "Hensel Phelps Logo"
  },
  {
    name: "Kier Construction",
    logo: "/trustedByLeadingCompanies/IC-Case-Study-Featured-Image-Kier-Construction-Logo-IC-700x299.webp",
    alt: "Kier Construction Logo"
  },

  {
    name: "Network Rail",
    logo: "/trustedByLeadingCompanies/network-rail-logo-png_seeklogo-323728.webp",
    alt: "Network Rail Logo"
  },
  {
    name: "Construction Partner",
    logo: "/trustedByLeadingCompanies/logo.webp",
    alt: "Construction Partner Logo"
  },
];

export default function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center gradient-bg overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-white/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-secondary-500/20 rounded-full blur-3xl animate-float animate-delay-300" />

        <div className="container-custom relative z-10 pt-32 pb-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white text-sm mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Now with GPT-4 Integration
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold text-white leading-tight">
                Build Smarter with{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                  AI-Powered
                </span>{" "}
                Construction
              </h1>

              <p className="mt-6 text-lg md:text-xl text-white/80 max-w-2xl">
                Transform your construction projects with intelligent waste detection,
                predictive analytics, and lean methodology tools. Reduce costs by up to 30%
                while building faster and more sustainably.
              </p>

              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link href="/signup" className="btn-primary text-lg px-8 py-4">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link href="/features" className="btn-secondary text-lg px-8 py-4 bg-white/10 border-white/30 text-white hover:bg-white/20">
                  See How It Works
                </Link>
              </div>

              <div className="mt-8 text-center lg:text-left">
                <Link
                  href="/login"
                  className="text-sm font-semibold text-white hover:text-primary-200 transition-colors"
                >
                  Already have an account? Sign In →
                </Link>
              </div>

              <div className="mt-10 flex items-center gap-6 justify-center lg:justify-start">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 border-2 border-white" />
                  ))}
                </div>
                <div className="text-white/80 text-sm">
                  <span className="font-semibold text-white">500+</span> construction teams trust us
                </div>
              </div>
            </div>

            {/* Hero Image/Dashboard Preview */}
            <div className="relative">
              <div className="relative bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-4 shadow-2xl">
                <div className="aspect-video bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl overflow-hidden">
                  <div className="p-4 space-y-4">
                    {/* Mock Dashboard Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                      </div>
                      <div className="text-white/60 text-xs">Lean AI Construction Dashboard</div>
                    </div>
                    {/* Mock Charts */}
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-white/5 rounded-lg p-3">
                        <div className="text-green-400 text-xs mb-1">Waste Reduced</div>
                        <div className="text-white text-lg font-bold">-32%</div>
                        <div className="mt-2 h-8 flex items-end gap-1">
                          {[40, 60, 45, 80, 65, 90, 75].map((h, i) => (
                            <div key={i} className="flex-1 bg-green-500/50 rounded-t" style={{ height: `${h}%` }} />
                          ))}
                        </div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <div className="text-blue-400 text-xs mb-1">On Schedule</div>
                        <div className="text-white text-lg font-bold">94%</div>
                        <div className="mt-2 h-8 flex items-end gap-1">
                          {[70, 75, 80, 85, 88, 92, 94].map((h, i) => (
                            <div key={i} className="flex-1 bg-blue-500/50 rounded-t" style={{ height: `${h}%` }} />
                          ))}
                        </div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <div className="text-purple-400 text-xs mb-1">Cost Savings</div>
                        <div className="text-white text-lg font-bold">$2.4M</div>
                        <div className="mt-2 h-8 flex items-end gap-1">
                          {[30, 45, 55, 60, 70, 85, 95].map((h, i) => (
                            <div key={i} className="flex-1 bg-purple-500/50 rounded-t" style={{ height: `${h}%` }} />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              {/* Floating Badge */}
              <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-xl p-4 flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">AI Analysis Complete</div>
                  <div className="text-xs text-gray-500">3 optimization opportunities found</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="#F9FAFB" />
          </svg>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="py-12 bg-gray-50">
        <div className="container-custom">
          <p className="text-center text-sm font-medium text-gray-500 mb-8">
            TRUSTED BY LEADING CONSTRUCTION COMPANIES
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 md:gap-12 items-center justify-items-center">
            {trustedBy.map((company) => (
              <div
                key={company.name}
                className="relative h-24 w-48 transition-all duration-300 ease-in-out hover:scale-110"
              >
                <Image
                  src={company.logo}
                  alt={company.alt}
                  fill
                  className="object-contain"
                  sizes="(max-width: 768px) 128px, 160px"
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-white">
        <div className="container-custom">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-100 mb-4">
                  <stat.icon className="w-8 h-8 text-primary-600" />
                </div>
                <div className="text-4xl md:text-5xl font-heading font-bold text-gray-900">
                  {stat.value}
                </div>
                <div className="mt-2 text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Everything you need to build{" "}
              <span className="gradient-text">smarter</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Our comprehensive platform combines AI technology with lean construction
              principles to help you deliver projects on time and under budget.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center">
            {features.map((feature) => (
              <div key={feature.name} className="card card-hover w-full max-w-sm">
                <div className={`w-12 h-12 rounded-xl ${feature.color} flex items-center justify-center mb-4`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
                  {feature.name}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link href="/features" className="btn-primary">
              Explore All Features
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section >

      {/* How It Works Section */}
      < section className="section-padding bg-white" >
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Get started in{" "}
              <span className="gradient-text">minutes</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Our platform is designed to be intuitive and easy to use.
              Here's how you can transform your construction projects.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Connect Your Data",
                description: "Import your existing project data or start fresh. Our platform integrates with popular tools like Procore, Autodesk, and more.",
              },
              {
                step: "02",
                title: "AI Analyzes Everything",
                description: "Our AI engine processes your data to identify waste, predict delays, and find optimization opportunities automatically.",
              },
              {
                step: "03",
                title: "Take Action & Save",
                description: "Receive actionable insights and recommendations. Implement changes and watch your efficiency and savings grow.",
              },
            ].map((item) => (
              <div key={item.step} className="relative">
                <div className="text-6xl font-heading font-bold text-primary-100 mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section >

      {/* Testimonials Section */}
      < section className="section-padding bg-gray-900" >
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-white">
              Loved by construction{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                professionals
              </span>
            </h2>
            <p className="mt-4 text-lg text-gray-400">
              See what our customers have to say about transforming their projects with Lean AI Construction.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gray-800 rounded-2xl p-8">
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6">
                  "{testimonial.content}"
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400" />
                  <div>
                    <div className="font-semibold text-white">{testimonial.author}</div>
                    <div className="text-sm text-gray-400">
                      {testimonial.role}, {testimonial.company}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section >

      {/* CTA Section */}
      < section className="section-padding bg-white" >
        <div className="container-custom">
          <div className="relative overflow-hidden rounded-3xl gradient-bg p-12 md:p-20">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }} />
            </div>

            <div className="relative z-10 text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-white">
                Ready to transform your construction projects?
              </h2>
              <p className="mt-6 text-lg md:text-xl text-white/80">
                Join 500+ construction teams already using Lean AI Construction to build smarter,
                faster, and more sustainably.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/signup" className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg px-8 py-4">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link href="/book-demo" className="btn-secondary border-white/30 text-white hover:bg-white/10 text-lg px-8 py-4">
                  Book a Demo
                </Link>
              </div>
              <p className="mt-6 text-sm text-white/60">
                No credit card required • 14-day free trial • Cancel anytime
              </p>
            </div>
          </div>
        </div>
      </section >
    </>
  );
}