import Link from "next/link";

export default function HelpPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container-custom py-24">
                <h1 className="text-4xl font-bold mb-8">Help Center</h1>

                <div className="max-w-4xl">
                    <p className="text-xl text-gray-600 mb-12">Get help with leanConstruction</p>

                    <div className="grid md:grid-cols-2 gap-8 mb-12">
                        <div className="bg-white p-6 rounded-xl shadow-sm">
                            <h3 className="text-xl font-semibold mb-3">Getting Started</h3>
                            <p className="text-gray-600 mb-4">Learn how to set up your account and start using leanConstruction.</p>
                            <Link href="/book-demo" className="text-primary-600 hover:text-primary-700 font-semibold">
                                Book a Demo →
                            </Link>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm">
                            <h3 className="text-xl font-semibold mb-3">Features</h3>
                            <p className="text-gray-600 mb-4">Explore all the features and capabilities of our platform.</p>
                            <Link href="/features" className="text-primary-600 hover:text-primary-700 font-semibold">
                                View Features →
                            </Link>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm">
                            <h3 className="text-xl font-semibold mb-3">Contact Support</h3>
                            <p className="text-gray-600 mb-4">Need personalized help? Our team is here to assist you.</p>
                            <Link href="/contact" className="text-primary-600 hover:text-primary-700 font-semibold">
                                Contact Us →
                            </Link>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm">
                            <h3 className="text-xl font-semibold mb-3">Pricing</h3>
                            <p className="text-gray-600 mb-4">Find the right plan for your construction business.</p>
                            <Link href="/pricing" className="text-primary-600 hover:text-primary-700 font-semibold">
                                View Pricing →
                            </Link>
                        </div>
                    </div>

                    <section className="bg-primary-50 p-8 rounded-xl">
                        <h2 className="text-2xl font-semibold mb-4">Frequently Asked Questions</h2>
                        <div className="space-y-4">
                            <details className="bg-white p-4 rounded-lg">
                                <summary className="font-semibold cursor-pointer">How do I get started?</summary>
                                <p className="mt-2 text-gray-600">Sign up for an account and book a demo to get personalized onboarding.</p>
                            </details>
                            <details className="bg-white p-4 rounded-lg">
                                <summary className="font-semibold cursor-pointer">What integrations are supported?</summary>
                                <p className="mt-2 text-gray-600">We integrate with Procore, Autodesk, Primavera P6, and many more construction tools.</p>
                            </details>
                            <details className="bg-white p-4 rounded-lg">
                                <summary className="font-semibold cursor-pointer">Is my data secure?</summary>
                                <p className="mt-2 text-gray-600">Yes, we use enterprise-grade security with encryption and regular backups.</p>
                            </details>
                        </div>
                    </section>
                </div>

                <div className="mt-12">
                    <Link href="/" className="text-primary-600 hover:text-primary-700 font-semibold">
                        ← Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}
