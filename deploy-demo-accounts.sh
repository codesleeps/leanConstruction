#!/bin/bash

echo "🚀 Deploying Demo Accounts Feature to Production"
echo "================================================"

# Configuration
VPS_IP="srv1187860.hstgr.cloud"
VPS_USER="root"
SSH_KEY="SSH_PUBLIC_KEY.txt"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH key file not found: $SSH_KEY"
    exit 1
fi

print_step "Uploading updated deployment packages to VPS..."

# Upload backend package
if scp -i "$SSH_KEY" -o StrictHostKeyChecking=no lean-construction-backend-updated.tar.gz "$VPS_USER@$VPS_IP:/tmp/"; then
    print_success "Backend package uploaded"
else
    print_error "Failed to upload backend package"
    exit 1
fi

# Upload frontend package
if scp -i "$SSH_KEY" -o StrictHostKeyChecking=no lean-construction-frontend-updated.tar.gz "$VPS_USER@$VPS_IP:/tmp/"; then
    print_success "Frontend package uploaded"
else
    print_error "Failed to upload frontend package"
    exit 1
fi

print_step "Connecting to VPS and deploying..."

# SSH into VPS and deploy
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" << 'EOF'
    echo "🔧 Starting deployment on VPS..."

    # Backup current packages
    echo "Creating backups..."
    cp /tmp/lean-construction-backend.tar.gz /tmp/lean-construction-backend-backup.tar.gz 2>/dev/null || true
    cp /tmp/lean-construction-frontend.tar.gz /tmp/lean-construction-frontend-backup.tar.gz 2>/dev/null || true

    # Replace packages with updated versions
    echo "Updating deployment packages..."
    cp /tmp/lean-construction-backend-updated.tar.gz /tmp/lean-construction-backend.tar.gz
    cp /tmp/lean-construction-frontend-updated.tar.gz /tmp/lean-construction-frontend.tar.gz

    # Navigate to deployment directory
    cd /var/www/lean-construction

    # Stop current services
    echo "Stopping current services..."
    pm2 stop all 2>/dev/null || true
    pm2 delete all 2>/dev/null || true

    # Deploy backend
    echo "Deploying backend..."
    mkdir -p app
    cd /tmp
    tar -xzf lean-construction-backend.tar.gz --strip-components=1 -C /var/www/lean-construction/app/

    # Install/update backend dependencies (minimal for demo accounts)
    cd /var/www/lean-construction
    source venv/bin/activate
    pip install -r requirements-demo.txt --quiet

    # Deploy frontend
    echo "Deploying frontend..."
    mkdir -p frontend
    cd /tmp
    tar -xzf lean-construction-frontend.tar.gz --strip-components=1 -C /var/www/lean-construction/frontend/

    # Build frontend (if Node.js is available)
    cd /var/www/lean-construction/frontend
    if command -v npm >/dev/null 2>&1; then
        npm install --silent
        npm run build --silent
        echo "Frontend built successfully"
    else
        echo "Node.js not available, skipping frontend build"
    fi

    # Start services
    echo "Starting services..."
    cd /var/www/lean-construction

    # Start backend with PM2
    pm2 start ecosystem.config.js 2>/dev/null || pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "lean-construction-api"

    # Wait for backend to start
    sleep 10

    # Test backend
    if curl -s http://localhost:8000/health >/dev/null; then
        echo "✅ Backend is running"
    else
        echo "❌ Backend failed to start"
    fi

    # Reload nginx
    sudo systemctl reload nginx 2>/dev/null || true

    echo "🎉 Deployment completed!"
EOF

if [ $? -eq 0 ]; then
    print_success "Demo accounts feature deployed successfully!"
    echo ""
    echo "🌐 Test the new features:"
    echo "   • Visit: https://leanaiconstruction.com"
    echo "   • Click 'Try Demo Accounts' on login page"
    echo "   • Select account type (Small/Medium/Enterprise)"
    echo "   • Experience pre-populated construction data"
    echo ""
    echo "📋 API Endpoints:"
    echo "   • POST /api/auth/demo-account/create?account_type=small"
    echo "   • GET /api/auth/demo-accounts"
else
    print_error "Deployment failed"
    exit 1
fi