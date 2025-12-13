#!/bin/bash

# ============================================
# Lean Construction AI - Backend Deployment Script
# ============================================

set -e

echo "🚀 Lean Construction AI - Backend Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running on VPS
if [[ $HOSTNAME == *"hstgr.cloud"* ]] || [[ $(hostname -I | grep -c "72.61.16.111") -gt 0 ]]; then
    print_success "Running on VPS environment"
else
    print_warning "Not running on VPS - some commands may not work"
    print_warning "This script should be run on: srv1187860.hstgr.cloud"
fi

echo ""
print_step "Step 1: Cleaning existing deployment..."
echo ""

# Clean up existing deployment
BACKEND_DIR="/var/www/lean-construction"
if [ -d "$BACKEND_DIR" ]; then
    echo "Removing existing deployment directory..."
    sudo rm -rf $BACKEND_DIR
fi

# Stop any running processes
pm2 delete lean-construction-api 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true

echo ""
print_step "Step 2: Creating directory structure..."
echo ""

# Create clean directory structure
sudo mkdir -p $BACKEND_DIR
sudo mkdir -p $BACKEND_DIR/logs
sudo chown -R $USER:$USER $BACKEND_DIR
sudo chmod -R 755 $BACKEND_DIR

print_success "Directory structure created"

echo ""
print_step "Step 3: Extracting backend package..."
echo ""

# Extract backend files
cd /tmp
if [ -f "lean-construction-backend.tar.gz" ]; then
    echo "Extracting backend package..."
    tar -xzf lean-construction-backend.tar.gz --strip-components=1 -C $BACKEND_DIR/
    print_success "Backend package extracted"
else
    print_error "Backend package not found at /tmp/lean-construction-backend.tar.gz"
    exit 1
fi

echo ""
print_step "Step 4: Creating Python virtual environment..."
echo ""

# Create Python virtual environment
cd $BACKEND_DIR
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo ""
print_step "Step 5: Installing dependencies..."
echo ""

# Upgrade pip
pip install --upgrade pip

# Install minimal production dependencies
pip install fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-decouple==3.8

print_success "Dependencies installed"

echo ""
print_step "Step 6: Testing backend import..."
echo ""

# Test import
cd $BACKEND_DIR
python -c "from app.main_lite import app; print('✅ Backend imports successfully!')"

print_success "Backend import test passed"

echo ""
print_step "Step 7: Configuring PM2..."
echo ""

# Create PM2 configuration
cat > $BACKEND_DIR/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: '/var/www/lean-construction/venv/bin/uvicorn',
    args: 'app.main_lite:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/lean-construction',
    interpreter: 'none',
    env: {
      PYTHONPATH: '/var/www/lean-construction',
      DATABASE_URL: 'sqlite:///./lean_construction.db',
      SECRET_KEY: 'production-secret-key-change-this',
      ENVIRONMENT: 'production'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/www/lean-construction/logs/pm2-error.log',
    out_file: '/var/www/lean-construction/logs/pm2-out.log',
    time: true
  }]
};
EOF

print_success "PM2 configuration created"

echo ""
print_step "Step 8: Starting backend service..."
echo ""

# Start with PM2
source venv/bin/activate
pm2 start $BACKEND_DIR/ecosystem.config.js
pm2 save
pm2 startup

print_success "Backend service started with PM2"

echo ""
print_step "Step 9: Verifying deployment..."
echo ""

# Wait for service to start
sleep 10

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "✅ Backend API is running successfully!"
    
    # Get health status
    HEALTH_STATUS=$(curl -s http://localhost:8000/health)
    echo "Health Check Response:"
    echo "$HEALTH_STATUS" | python -m json.tool
else
    print_error "❌ Backend API is not responding"
    echo "Checking PM2 logs..."
    pm2 logs lean-construction-api --lines 50
    exit 1
fi

echo ""
print_step "Step 10: Configuring monitoring..."
echo ""

# Create health check script
sudo tee /usr/local/bin/lean-construction-healthcheck.sh > /dev/null <<'HEALTHCHECK'
#!/bin/bash

API_URL="http://localhost:8000/health"

if ! curl -f -s "$API_URL" > /dev/null; then
    echo "[$(date)] Backend health check failed, restarting..." >> /var/log/lean-construction-health.log
    pm2 restart lean-construction-api
    sleep 10
    if ! curl -f -s "$API_URL" > /dev/null; then
        echo "[$(date)] Restart failed, trying systemd..." >> /var/log/lean-construction-health.log
        sudo systemctl restart lean-construction-backend
    fi
fi
HEALTHCHECK

sudo chmod +x /usr/local/bin/lean-construction-healthcheck.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/lean-construction-healthcheck.sh") | crontab -

print_success "Health check monitoring configured"

echo ""
print_step "Step 11: Configuring systemd service..."
echo ""

# Create systemd service
sudo tee /etc/systemd/system/lean-construction-backend.service > /dev/null <<'SYSTEMD'
[Unit]
Description=Lean Construction AI Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/lean-construction
Environment="PYTHONPATH=/var/www/lean-construction"
ExecStart=/var/www/lean-construction/venv/bin/uvicorn app.main_lite:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:/var/www/lean-construction/logs/backend.log
StandardError=append:/var/www/lean-construction/logs/backend-error.log

[Install]
WantedBy=multi-user.target
SYSTEMD

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable lean-construction-backend

print_success "Systemd service configured"

echo ""
echo "🎉 Backend Deployment Complete!"
echo "=============================="
echo ""
echo "📊 Deployment Summary:"
echo "✅ Backend API: Running on port 8000"
echo "✅ Health Check: http://localhost:8000/health"
echo "✅ API Docs: http://localhost:8000/docs"
echo "✅ PM2 Process Manager: Active"
echo "✅ Health Monitoring: Configured (runs every 5 minutes)"
echo "✅ Systemd Service: Configured as backup"
echo ""
echo "📋 Management Commands:"
echo "• Check status: pm2 status"
echo "• View logs: pm2 logs lean-construction-api"
echo "• Restart: pm2 restart lean-construction-api"
echo "• Stop: pm2 stop lean-construction-api"
echo "• Start: pm2 start lean-construction-api"
echo ""
echo "⚠️  Next Steps:"
echo "1. Configure Nginx reverse proxy"
echo "2. Set up environment variables in .env file"
echo "3. Test external access via VPS IP"
echo "4. Configure DNS and SSL certificates"
echo ""
