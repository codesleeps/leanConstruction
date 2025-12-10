# Lean AI Construction - Marketing Website

This is the marketing/landing website for Lean AI Construction, built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Modern Design**: Clean, professional design with smooth animations
- **Responsive**: Fully responsive across all device sizes
- **SEO Optimized**: Built-in SEO with Next.js metadata API
- **Performance**: Optimized for Core Web Vitals
- **Accessibility**: WCAG compliant components

## Pages

- **Home** (`/`) - Landing page with hero, features, testimonials, and CTA
- **Features** (`/features`) - Detailed product features and integrations
- **Pricing** (`/pricing`) - Pricing plans with comparison table
- **About** (`/about`) - Company story, team, and values
- **Contact** (`/contact`) - Contact form and office locations

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to the website directory
cd website

# Install dependencies
npm install

# Start development server
npm run dev
```

The site will be available at `http://localhost:3000`

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Project Structure

```
website/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx           # Home page
│   │   ├── layout.tsx         # Root layout
│   │   ├── globals.css        # Global styles
│   │   ├── features/          # Features page
│   │   ├── pricing/           # Pricing page
│   │   ├── about/             # About page
│   │   └── contact/           # Contact page
│   └── components/
│       └── layout/
│           ├── Header.tsx     # Navigation header
│           └── Footer.tsx     # Site footer
├── public/                     # Static assets
├── tailwind.config.ts         # Tailwind configuration
├── next.config.mjs            # Next.js configuration
└── package.json
```

## Deployment

### Vercel (Recommended)

The easiest way to deploy is using Vercel:

```bash
npm i -g vercel
vercel
```

### Docker

A Dockerfile can be created for containerized deployment:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

### VPS Deployment

For deployment to the existing VPS alongside the dashboard:

1. Build the website: `npm run build`
2. Copy the `.next` folder and `package.json` to the VPS
3. Configure nginx to serve the website on the main domain
4. The dashboard can be served on a subdomain (e.g., `app.leanaiconstruction.com`)

## Environment Variables

Create a `.env.local` file for local development:

```env
# Analytics (optional)
NEXT_PUBLIC_GA_ID=your-google-analytics-id

# Contact form (optional)
CONTACT_FORM_ENDPOINT=your-form-endpoint
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

Proprietary - Lean AI Construction