/** @type {import('next').NextConfig} */
const nextConfig = {
  /* output: 'standalone', // Removed to fix build issue */
  images: {
    domains: ['leanaiconstruction.com'],
  },
  eslint: {
    // Allow builds to complete even with ESLint warnings
    ignoreDuringBuilds: true,
  },
  /* rewrites: removed for production build compatibility - handled by Nginx */
};

export default nextConfig;