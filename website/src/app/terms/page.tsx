import Link from "next/link";

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container-custom py-24">
                <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>

                <div className="prose prose-lg max-w-4xl">
                    <p className="text-gray-600 mb-8">Last updated: December 15, 2025</p>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
                        <p>By accessing and using leanConstruction, you accept and agree to be bound by the terms and provision of this agreement.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">2. Use License</h2>
                        <p>Permission is granted to temporarily access the materials on leanConstruction for personal, non-commercial transitory viewing only.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">3. User Responsibilities</h2>
                        <p>Users are responsible for maintaining the confidentiality of their account information and for all activities under their account.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">4. Service Modifications</h2>
                        <p>We reserve the right to modify or discontinue the service at any time without notice.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">5. Contact</h2>
                        <p>For questions about these Terms, please <Link href="/contact" className="text-primary-600 hover:text-primary-700">contact us</Link>.</p>
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
