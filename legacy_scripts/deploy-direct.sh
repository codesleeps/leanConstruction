#!/bin/bash

echo "🚀 Direct Demo Accounts Deployment"
echo "=================================="

# Configuration
VPS_IP="srv1187860.hstgr.cloud"
VPS_USER="root"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create deployment package
print_step "Creating deployment package..."
mkdir -p /tmp/demo-deploy
cp -r backend/* /tmp/demo-deploy/
cp -r frontend/* /tmp/demo-deploy/frontend/

# Copy minimal requirements
cp backend/requirements-demo.txt /tmp/demo-deploy/requirements.txt

# Create tarball
cd /tmp
tar -czf demo-deploy.tar.gz demo-deploy/

print_step "Uploading deployment package..."
if scp -o StrictHostKeyChecking=no demo-deploy.tar.gz "$VPS_USER@$VPS_IP:/tmp/"; then
    print_success "Package uploaded"
else
    print_error "Upload failed"
    exit 1
fi

print_step "Deploying on VPS..."
ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" << 'EOF'
    echo "Starting deployment on VPS..."

    cd /var/www/lean-construction

    # Backup current setup
    echo "Creating backup..."
    mkdir -p /tmp/backup
    cp -r app/* /tmp/backup/ 2>/dev/null || true
    cp -r frontend/* /tmp/backup/frontend/ 2>/dev/null || true

    # Extract new code
    echo "Extracting new code..."
    cd /tmp
    tar -xzf demo-deploy.tar.gz

    # Deploy backend
    echo "Deploying backend..."
    mkdir -p /var/www/lean-construction/app
    cp -r demo-deploy/* /var/www/lean-construction/app/

    # Install dependencies
    cd /var/www/lean-construction
    source venv/bin/activate
    pip install -r requirements.txt

    # Deploy frontend
    echo "Deploying frontend..."
    mkdir -p /var/www/lean-construction/frontend
    cp -r demo-deploy/frontend/* /var/www/lean-construction/frontend/

    # Build frontend
    cd /var/www/lean-construction/frontend
    if command -v npm >/dev/null 2>&1; then
        npm install
        npm run build
    fi

    # Restart services
    cd /var/www/lean-construction
    pm2 restart all 2>/dev/null || pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "lean-construction-api"
    sudo systemctl reload nginx 2>/dev/null || true

    echo "✅ Deployment completed!"
EOF

if [ $? -eq 0 ]; then
    print_success "Demo accounts deployed successfully!"
    echo ""
    echo "🌐 Test at: https://leanaiconstruction.com"
    echo "   • Click 'Try Demo Accounts'"
    echo "   • Select account type"
    echo "   • Experience instant access!"
else
    print_error "Deployment failed"
fi

# Cleanup
rm -rf /tmp/demo-deploy /tmp/demo-deploy.tar.gz