#!/bin/bash

# ============================================
# Comprehensive Backend Deployment Fix
# ============================================

set -e

echo "🔧 Starting Backend Deployment Fix"
echo "=================================="

# Configuration
BACKEND_DIR="/var/www/lean-construction"
LOG_FILE="/tmp/deployment-fix.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting backend deployment fix..."

# Step 1: Clean up existing deployment
log "Step 1: Cleaning up existing deployment..."
if [ -d "$BACKEND_DIR" ]; then
    log "Removing existing deployment directory..."
    sudo rm -rf $BACKEND_DIR
fi

# Step 2: Create clean directory structure
log "Step 2: Creating clean directory structure..."
sudo mkdir -p $BACKEND_DIR
sudo mkdir -p $BACKEND_DIR/logs

# Step 3: Extract backend files
log "Step 3: Extracting backend files..."
cd /tmp

if [ -f "lean-construction-backend-fixed.tar.gz" ]; then
    log "Using fixed backend package..."
    tar -xzf lean-construction-backend-fixed.tar.gz --strip-components=1 -C $BACKEND_DIR/
elif [ -f "lean-construction-backend.tar.gz" ]; then
    log "Using standard backend package..."
    tar -xzf lean-construction-backend.tar.gz --strip-components=1 -C $BACKEND_DIR/
else
    log "Error: No backend package found!"
    exit 1
fi

# Step 4: Extract frontend files
log "Step 4: Extracting frontend files..."
if [ -f "lean-construction-frontend.tar.gz" ]; then
    mkdir -p $BACKEND_DIR/frontend
    tar -xzf lean-construction-frontend.tar.gz --strip-components=1 -C $BACKEND_DIR/frontend/
else
    log "Warning: Frontend package not found, skipping frontend extraction"
fi

# Step 5: Set proper permissions
log "Step 5: Setting proper permissions..."
sudo chown -R $USER:$USER $BACKEND_DIR
sudo chmod -R 755 $BACKEND_DIR

# Step 6: Create Python virtual environment
log "Step 6: Creating Python virtual environment..."
cd $BACKEND_DIR

if [ ! -d "venv" ]; then
    log "Creating new virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Step 7: Install dependencies
log "Step 7: Installing dependencies..."
pip install --break-system-packages --upgrade pip

if [ -f "requirements.txt" ]; then
    log "Installing from requirements.txt..."
    pip install --break-system-packages -r requirements.txt
else
    log "Installing minimal dependencies..."
    pip install --break-system-packages fastapi uvicorn[standard] python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv
fi

# Step 8: Test basic imports
log "Step 8: Testing basic imports..."
cd $BACKEND_DIR

# Test minimal backend first
if [ -f "minimal_backend.py" ]; then
    log "Testing minimal backend..."
    python minimal_backend.py &
    MINIMAL_PID=$!
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null; then
        log "✅ Minimal backend is working!"
        kill $MINIMAL_PID 2>/dev/null || true
    else
        log "❌ Minimal backend test failed"
        kill $MINIMAL_PID 2>/dev/null || true
    fi
fi

# Step 9: Test full backend if available
log "Step 9: Testing full backend..."
if [ -f "app/main.py" ]; then
    log "Testing full backend..."
    cd app
    python -c "from main import app; print('✅ Full backend imports successfully!')" 2>/dev/null && log "✅ Full backend import test passed!" || log "❌ Full backend import test failed"
fi

# Step 10: Create PM2 configuration
log "Step 10: Creating PM2 configuration..."

cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: 'uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000 --reload',
    cwd: '/var/www/lean-construction',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production',
      PORT: 8000,
      PYTHONPATH: '/var/www/lean-construction'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '2G',
    error_file: '/var/www/lean-construction/logs/pm2-error.log',
    out_file: '/var/www/lean-construction/logs/pm2-out.log',
    log_file: '/var/www/lean-construction/logs/pm2-combined.log',
    time: true
  }]
};
EOF

# Step 11: Start services
log "Step 11: Starting services..."

# Stop any existing processes
pm2 delete lean-construction-api 2>/dev/null || true

# Start with PM2
source venv/bin/activate
pm2 start ecosystem.config.js
pm2 save

# Step 12: Verify deployment
log "Step 12: Verifying deployment..."
sleep 10

if curl -s http://localhost:8000/health > /dev/null; then
    log "✅ Backend API is running successfully!"
    log "✅ Deployment fix completed successfully!"
    
    echo ""
    echo "🎉 Backend Deployment Fixed!"
    echo "=========================="
    echo "✅ API Status: Running"
    echo "✅ Health Check: Available at http://localhost:8000/health"
    echo "✅ API Docs: Available at http://localhost:8000/docs"
    echo ""
    echo "Next Steps:"
    echo "1. Run frontend deployment"
    echo "2. Configure DNS records"
    echo "3. Install SSL certificates"
    echo ""
else
    log "❌ Backend API is not responding"
    log "Checking PM2 logs..."
    pm2 logs lean-construction-api --lines 20
    exit 1
fi

log "Deployment fix completed!"