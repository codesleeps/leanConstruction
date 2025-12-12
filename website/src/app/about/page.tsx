import Link from "next/link";
import {
  ArrowRight,
  Target,
  Heart,
  Lightbulb,
  Users,
  Award,
  Globe,
  TrendingUp
} from "lucide-react";

const values = [
  {
    name: "Innovation",
    description: "We constantly push the boundaries of what's possible with AI and construction technology.",
    icon: Lightbulb,
  },
  {
    name: "Sustainability",
    description: "We're committed to reducing waste and building a more sustainable construction industry.",
    icon: Heart,
  },
  {
    name: "Excellence",
    description: "We strive for excellence in everything we do, from our product to our customer service.",
    icon: Target,
  },
  {
    name: "Collaboration",
    description: "We believe in the power of teamwork and partnership to achieve great things.",
    icon: Users,
  },
];

const stats = [
  { value: "500+", label: "Construction Teams" },
  { value: "$50M+", label: "Cost Savings Generated" },
  { value: "12", label: "Countries" },
  { value: "98%", label: "Customer Satisfaction" },
];

const team = [
  {
    name: "James Mitchell",
    role: "CEO & Co-Founder",
    bio: "Former construction project manager with 15 years of experience. Passionate about bringing technology to the construction industry.",
  },
  {
    name: "Dr. Sarah Chen",
    role: "CTO & Co-Founder",
    bio: "PhD in Machine Learning from MIT. Previously led AI research at a major tech company. Expert in computer vision and predictive analytics.",
  },
  {
    name: "Michael Roberts",
    role: "VP of Engineering",
    bio: "20 years of software engineering experience. Former engineering director at a Fortune 500 company.",
  },
  {
    name: "Emma Thompson",
    role: "VP of Customer Success",
    bio: "Background in construction management and customer experience. Dedicated to helping customers achieve their goals.",
  },
  {
    name: "David Park",
    role: "Head of Product",
    bio: "Product leader with experience at multiple successful startups. Focused on building products that solve real problems.",
  },
  {
    name: "Lisa Anderson",
    role: "Head of Sales",
    bio: "15 years in enterprise sales. Passionate about helping construction companies transform their operations.",
  },
];

const milestones = [
  {
    year: "2020",
    title: "Company Founded",
    description: "Lean AI Construction was founded with a mission to revolutionize the construction industry through AI.",
  },
  {
    year: "2021",
    title: "Seed Funding",
    description: "Raised $5M in seed funding to accelerate product development and expand the team.",
  },
  {
    year: "2022",
    title: "Product Launch",
    description: "Launched our first product with AI-powered waste detection and predictive analytics.",
  },
  {
    year: "2023",
    title: "Series A",
    description: "Raised $25M Series A to scale operations and expand into new markets.",
  },
  {
    year: "2024",
    title: "Global Expansion",
    description: "Expanded to 12 countries and reached 500+ construction teams using our platform.",
  },
];

export default function AboutPage() {
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
              Building the future of{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                construction
              </span>
            </h1>
            <p className="mt-6 text-lg md:text-xl text-white/80">
              We're on a mission to transform the construction industry through AI-powered
              technology and lean methodology, making projects more efficient, sustainable, and profitable.
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

      {/* Mission Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
                Our Mission
              </h2>
              <p className="mt-6 text-lg text-gray-600 leading-relaxed">
                The construction industry is responsible for nearly 40% of global waste.
                We believe technology can change that. Our mission is to empower construction
                teams with AI-powered tools that reduce waste, improve efficiency, and deliver
                better outcomes for everyone involved.
              </p>
              <p className="mt-4 text-lg text-gray-600 leading-relaxed">
                By combining cutting-edge artificial intelligence with proven lean construction
                methodologies, we're helping teams build smarter, faster, and more sustainably
                than ever before.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-6">
              {stats.map((stat) => (
                <div key={stat.label} className="bg-white rounded-2xl p-6 shadow-lg text-center">
                  <div className="text-3xl md:text-4xl font-heading font-bold text-primary-600">
                    {stat.value}
                  </div>
                  <div className="mt-2 text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Our{" "}
              <span className="gradient-text">Values</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              These core values guide everything we do, from product development to customer relationships.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value) => (
              <div key={value.name} className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-primary-100 flex items-center justify-center mx-auto mb-4">
                  <value.icon className="w-8 h-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-heading font-semibold text-gray-900">
                  {value.name}
                </h3>
                <p className="mt-2 text-gray-600">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Story/Timeline Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Our{" "}
              <span className="gradient-text">Journey</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              From a small startup to a global platform, here's how we've grown.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-primary-200" />

              {milestones.map((milestone, index) => (
                <div key={milestone.year} className="relative flex gap-8 pb-12 last:pb-0">
                  {/* Year bubble */}
                  <div className="relative z-10 w-16 h-16 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-sm">{milestone.year}</span>
                  </div>

                  {/* Content */}
                  <div className="bg-white rounded-xl p-6 shadow-lg flex-1">
                    <h3 className="text-xl font-heading font-semibold text-gray-900">
                      {milestone.title}
                    </h3>
                    <p className="mt-2 text-gray-600">
                      {milestone.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900">
              Meet our{" "}
              <span className="gradient-text">Team</span>
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              We're a diverse team of engineers, construction experts, and innovators
              united by a common goal.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {team.map((member) => (
              <div key={member.name} className="bg-gray-50 rounded-2xl p-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 mx-auto mb-4" />
                <div className="text-center">
                  <h3 className="text-xl font-heading font-semibold text-gray-900">
                    {member.name}
                  </h3>
                  <p className="text-primary-600 font-medium">{member.role}</p>
                  <p className="mt-3 text-gray-600 text-sm">
                    {member.bio}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Awards & Recognition */}
      <section className="section-padding bg-gray-900">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-white">
              Awards &{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-green-300">
                Recognition
              </span>
            </h2>
            <p className="mt-4 text-lg text-gray-400">
              We're honored to be recognized by industry leaders for our innovation and impact.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: "Best Construction Tech Startup 2023", org: "Construction Technology Awards" },
              { title: "AI Innovation Award", org: "Tech Innovation Summit" },
              { title: "Sustainability Leader", org: "Green Building Council" },
            ].map((award) => (
              <div key={award.title} className="bg-gray-800 rounded-2xl p-8 text-center">
                <Award className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                <h3 className="text-xl font-heading font-semibold text-white">
                  {award.title}
                </h3>
                <p className="mt-2 text-gray-400">{award.org}</p>
              </div>
            ))}
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
                Join us in building the future
              </h2>
              <p className="mt-6 text-lg md:text-xl text-white/80">
                Whether you're looking to transform your construction projects or join our team,
                we'd love to hear from you.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/signup" className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg px-8 py-4">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link href="/careers" className="btn-secondary border-white/30 text-white hover:bg-white/10 text-lg px-8 py-4">
                  View Careers
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}