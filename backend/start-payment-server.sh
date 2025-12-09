#!/bin/bash

# Payment-Only Server Startup Script
# This script starts a lightweight payment-only server without heavy ML dependencies

set -e

echo "🚀 Starting Payment-Only Server..."
echo "📋 This server includes only payment endpoints (no ML dependencies)"
echo ""

# Check if we're in the right directory
if [ ! -f "app/payments_only.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: app/payments_only.py"
    exit 1
fi

# Install minimal dependencies if not already installed
echo "📦 Installing minimal dependencies..."
pip install -r requirements-minimal.txt

# Start the payment-only server
echo "🌐 Starting payment-only server on http://localhost:8000"
echo "📖 API documentation available at http://localhost:8000/docs"
echo "💳 Payment endpoints prefix: /api/v1/payments"
echo ""
echo "Available endpoints:"
echo "  POST /api/v1/payments/create-subscription"
echo "  POST /api/v1/payments/confirm-subscription"
echo "  GET  /api/v1/payments/subscription-status/{customer_id}"
echo "  POST /api/v1/payments/cancel-subscription"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

cd app
python payments_only.py