import Link from "next/link";
import {
  ArrowRight,
  Check,
  X,
  HelpCircle,
  Building2,
  Users,
  Rocket
} from "lucide-react";

const tiers = [
  {
    name: "Starter",
    id: "starter",
    price: { monthly: 99, annual: 79 },
    description: "Perfect for small teams getting started with lean construction.",
    icon: Rocket,
    features: [
      { name: "Up to 5 team members", included: true },
      { name: "3 active projects", included: true },
      { name: "Basic waste detection", included: true },
      { name: "Standard dashboards", included: true },
      { name: "Email support", included: true },
      { name: "Mobile app access", included: true },
      { name: "Predictive analytics", included: false },
      { name: "Custom integrations", included: false },
      { name: "API access", included: false },
      { name: "SSO/SAML", included: false },
    ],
    cta: "Start Free Trial",
    popular: false,
  },
  {
    name: "Professional",
    id: "professional",
    price: { monthly: 299, annual: 249 },
    description: "For growing teams that need advanced features and analytics.",
    icon: Users,
    features: [
      { name: "Up to 25 team members", included: true },
      { name: "Unlimited projects", included: true },
      { name: "Advanced waste detection", included: true },
      { name: "Custom dashboards", included: true },
      { name: "Priority support", included: true },
      { name: "Mobile app access", included: true },
      { name: "Predictive analytics", included: true },
      { name: "Standard integrations", included: true },
      { name: "API access", included: true },
      { name: "SSO/SAML", included: false },
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    id: "enterprise",
    price: { monthly: null, annual: null },
    description: "For large organizations with custom requirements and dedicated support.",
    icon: Building2,
    features: [
      { name: "Unlimited team members", included: true },
      { name: "Unlimited projects", included: true },
      { name: "AI-powered waste detection", included: true },
      { name: "Custom dashboards & reports", included: true },
      { name: "24/7 dedicated support", included: true },
      { name: "Mobile app access", included: true },
      { name: "Advanced predictive analytics", included: true },
      { name: "Custom integrations", included: true },
      { name: "Full API access", included: true },
      { name: "SSO/SAML & SCIM", included: true },
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

const faqs = [
  {
    question: "How does the free trial work?",
    answer: "Start with a 14-day free trial of any plan. No credit card required. You'll have full access to all features in your chosen plan. At the end of the trial, you can choose to subscribe or your account will be downgraded to a limited free tier.",
  },
  {
    question: "Can I change plans later?",
    answer: "Yes, you can upgrade or downgrade your plan at any time. When upgrading, you'll be charged the prorated difference. When downgrading, the new rate will apply at your next billing cycle.",
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards (Visa, MasterCard, American Express), as well as bank transfers for annual Enterprise plans. All payments are processed securely through Stripe.",
  },
  {
    question: "Is there a discount for annual billing?",
    answer: "Yes! When you choose annual billing, you save approximately 20% compared to monthly billing. This discount is automatically applied when you select the annual option.",
  },
  {
    question: "What happens to my data if I cancel?",
    answer: "Your data remains accessible for 30 days after cancellation. During this period, you can export all your data. After 30 days, data is permanently deleted in accordance with our privacy policy.",
  },
  {
    question: "Do you offer discounts for non-profits?",
    answer: "Yes, we offer a 25% discount for registered non-profit organizations. Contact our sales team with proof of non-profit status to apply for the discount.",
  },
];

const comparisonFeatures = [
  { name: "Team Members", starter: "Up to 5", professional: "Up to 25", enterprise: "Unlimited" },
  { name: "Active Projects", starter: "3", professional: "Unlimited", enterprise: "Unlimited" },
  { name: "Waste Detection", starter: "Basic", professional: "Advanced", enterprise: "AI-Powered" },
  { name: "Predictive Analytics", starter: "—", professional: "✓", enterprise: "Advanced" },
  { name: "Custom Dashboards", starter: "—", professional: "✓", enterprise: "✓" },
  { name: "API Access", starter: "—", professional: "✓", enterprise: "Full" },
  { name: "Integrations", starter: "Basic", professional: "Standard", enterprise: "Custom" },
  { name: "Support", starter: "Email", professional: "Priority", enterprise: "24/7 Dedicated" },
  { name: "SSO/SAML", starter: "—", professional: "—", enterprise: "✓" },
  { name: "Data Retention", starter: "1 year", professional: "3 years", enterprise: "Unlimited" },
  { name: "Training", starter: "Self-serve", professional: "Webinars", enterprise: "On-site" },
  { name: "SLA", starter: "99%", professional: "99.5%", enterprise: "99.9%" },
];

export default function PricingPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 gradient-bg overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <div className="container-custom relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold text-white">
              Simple, transparent{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                pricing
              </span>
            </h1>
            <p className="mt-6 text-lg md:text-xl text-white/80">
              Choose the plan that fits your team. All plans include a 14-day free trial.
              No credit card required.
            </p>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="#F9FAFB" />
          </svg>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-12">
            <span className="text-gray-600">Monthly</span>
            <button className="relative w-14 h-8 bg-primary-600 rounded-full transition-colors">
              <span className="absolute right-1 top-1 w-6 h-6 bg-white rounded-full shadow-sm transition-transform" />
            </button>
            <span className="text-gray-900 font-medium">Annual</span>
            <span className="ml-2 px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
              Save 20%
            </span>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {tiers.map((tier) => (
              <div
                key={tier.id}
                className={`relative bg-white rounded-2xl shadow-xl overflow-hidden ${tier.popular ? 'ring-2 ring-primary-500' : ''
                  }`}
              >
                {tier.popular && (
                  <div className="absolute top-0 left-0 right-0 bg-primary-500 text-white text-center text-sm font-medium py-2">
                    Most Popular
                  </div>
                )}

                <div className={`p-8 ${tier.popular ? 'pt-14' : ''}`}>
                  <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center mb-4">
                    <tier.icon className="w-6 h-6 text-primary-600" />
                  </div>

                  <h3 className="text-2xl font-heading font-bold text-gray-900">
                    {tier.name}
                  </h3>
                  <p className="mt-2 text-gray-600 text-sm">
                    {tier.description}
                  </p>

                  <div className="mt-6">
                    {tier.price.monthly ? (
                      <>
                        <span className="text-4xl font-heading font-bold text-gray-900">
                          ${tier.price.annual}
                        </span>
                        <span className="text-gray-500">/month</span>
                        <p className="text-sm text-gray-500 mt-1">
                          billed annually (${tier.price.annual * 12}/year)
                        </p>
                      </>
                    ) : (
                      <span className="text-4xl font-heading font-bold text-gray-900">
                        Custom
                      </span>
                    )}
                  </div>

                  <Link
                    href={tier.price.monthly ? "/signup" : "/contact"}
                    className={`mt-8 w-full flex items-center justify-center px-6 py-3 rounded-lg font-semibold transition-all ${tier.popular
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                      }`}
                  >
                    {tier.cta}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </div>

                <div className="px-8 pb-8">
                  <div className="border-t border-gray-100 pt-8">
                    <h4 className="text-sm font-semibold text-gray-900 mb-4">
                      What's included:
                    </h4>
                    <ul className="space-y-3">
                      {tier.features.map((feature) => (
                        <li key={feature.name} className="flex items-start gap-3">
                          {feature.included ? (
                            <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                          ) : (
                            <X className="w-5 h-5 text-gray-300 flex-shrink-0" />
                          )}
                          <span className={feature.included ? 'text-gray-700' : 'text-gray-400'}>
                            {feature.name}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Compare{" "}
              <span className="gradient-text">plans</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              See a detailed comparison of what's included in each plan.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[800px]">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-4 px-6 font-heading font-semibold text-gray-900">
                    Feature
                  </th>
                  <th className="text-center py-4 px-6 font-heading font-semibold text-gray-900">
                    Starter
                  </th>
                  <th className="text-center py-4 px-6 font-heading font-semibold text-primary-600 bg-primary-50 rounded-t-lg">
                    Professional
                  </th>
                  <th className="text-center py-4 px-6 font-heading font-semibold text-gray-900">
                    Enterprise
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonFeatures.map((feature, index) => (
                  <tr key={feature.name} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                    <td className="py-4 px-6 text-gray-700">{feature.name}</td>
                    <td className="py-4 px-6 text-center text-gray-600">{feature.starter}</td>
                    <td className="py-4 px-6 text-center text-gray-900 font-medium bg-primary-50/50">
                      {feature.professional}
                    </td>
                    <td className="py-4 px-6 text-center text-gray-600">{feature.enterprise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Frequently asked{" "}
              <span className="gradient-text">questions</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Have questions? We've got answers. If you can't find what you're looking for,
              feel free to contact our support team.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="grid gap-6">
              {faqs.map((faq) => (
                <div key={faq.question} className="bg-white rounded-xl p-6 shadow-sm">
                  <h3 className="flex items-start gap-3 font-heading font-semibold text-gray-900">
                    <HelpCircle className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                    {faq.question}
                  </h3>
                  <p className="mt-3 text-gray-600 pl-8">
                    {faq.answer}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="relative overflow-hidden rounded-3xl gradient-bg p-12 md:p-20">
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }} />
            </div>

            <div className="relative z-10 text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-heading font-bold text-white">
                Still have questions?
              </h2>
              <p className="mt-6 text-lg md:text-xl text-white/80">
                Our team is here to help. Schedule a demo to see how Lean AI Construction
                can transform your projects.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/book-demo" className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg px-8 py-4">
                  Schedule a Demo
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link href="/signup" className="btn-secondary border-white/30 text-white hover:bg-white/10 text-lg px-8 py-4">
                  Start Free Trial
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}