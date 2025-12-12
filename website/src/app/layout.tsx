import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { BackToTop } from "@/components/ui/BackToTop";
import { ChatWidget } from "@/components/ui/ChatWidget";

export const metadata: Metadata = {
  title: "Lean AI Construction - AI-Powered Construction Management",
  description: "Transform your construction projects with AI-powered waste detection, predictive analytics, and lean methodology tools. Reduce costs by up to 30% and improve efficiency.",
  keywords: "construction management, AI, lean construction, waste detection, predictive analytics, project management, construction software",
  authors: [{ name: "Lean AI Construction" }],
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    title: "Lean AI Construction - AI-Powered Construction Management",
    description: "Transform your construction projects with AI-powered waste detection, predictive analytics, and lean methodology tools.",
    url: "https://leanaiconstruction.com",
    siteName: "Lean AI Construction",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Lean AI Construction Platform",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Lean AI Construction - AI-Powered Construction Management",
    description: "Transform your construction projects with AI-powered waste detection, predictive analytics, and lean methodology tools.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="flex-grow">
          {children}
        </main>
        <Footer />
        <BackToTop />
        <ChatWidget />
      </body>
    </html>
  );
}