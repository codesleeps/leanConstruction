import Link from "next/link";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container-custom py-24">
                <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>

                <div className="prose prose-lg max-w-4xl">
                    <p className="text-gray-600 mb-8">Last updated: December 15, 2025</p>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
                        <p>We collect information you provide directly, such as when you create an account, contact us, or use our services.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
                        <p>We use the information we collect to provide, maintain, and improve our services, and to communicate with you.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">3. Data Security</h2>
                        <p>We implement appropriate security measures to protect your personal information from unauthorized access.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">4. Data Retention</h2>
                        <p>We retain your information for as long as your account is active or as needed to provide services.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">5. Your Rights</h2>
                        <p>You have the right to access, update, or delete your personal information at any time.</p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">6. Contact Us</h2>
                        <p>If you have questions about this Privacy Policy, please <Link href="/contact" className="text-primary-600 hover:text-primary-700">contact us</Link>.</p>
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
