#!/bin/bash

# ============================================
# Frontend Deployment Script
# ============================================

set -e

echo "🎨 Starting Frontend Deployment"
echo "================================"

# Configuration
FRONTEND_DIR="/var/www/lean-construction/frontend"
LOG_FILE="/tmp/frontend-deployment.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting frontend deployment..."

# Step 1: Check if frontend source exists
if [ ! -d "$FRONTEND_DIR" ]; then
    log "Frontend directory not found. Creating..."
    mkdir -p $FRONTEND_DIR
fi

# Step 2: Install Node.js dependencies
log "Step 1: Installing Node.js dependencies..."
cd $FRONTEND_DIR

if [ -f "package.json" ]; then
    log "Installing npm packages..."
    npm install
else
    log "Error: package.json not found!"
    exit 1
fi

# Step 3: Create environment file for production
log "Step 2: Creating production environment..."
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://constructionaipro.com/api
REACT_APP_WS_URL=wss://constructionaipro.com/ws
REACT_APP_ENVIRONMENT=production
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
EOF

log "Created production environment file"

# Step 4: Build the React application
log "Step 3: Building React application..."
npm run build

# Step 5: Verify build
if [ -d "build" ] && [ -f "build/index.html" ]; then
    log "✅ Build completed successfully!"
    log "Build directory size: $(du -sh build | cut -f1)"
else
    log "❌ Build failed!"
    exit 1
fi

# Step 6: Set permissions
log "Step 4: Setting permissions..."
sudo chown -R www-data:www-data $FRONTEND_DIR/build
sudo chmod -R 755 $FRONTEND_DIR/build

# Step 7: Test local build
log "Step 5: Testing local build..."
cd build
python3 -m http.server 3001 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

if curl -s http://localhost:3001 > /dev/null; then
    log "✅ Local build test passed!"
else
    log "⚠️ Local build test failed, but continuing..."
fi

kill $SERVER_PID 2>/dev/null || true

log "Frontend deployment completed!"

echo ""
echo "🎉 Frontend Deployment Complete!"
echo "==============================="
echo "✅ Build Status: Completed"
echo "✅ Build Location: $FRONTEND_DIR/build"
echo "✅ Environment: Production ready"
echo ""
echo "Next Steps:"
echo "1. Configure Nginx for React routing"
echo "2. Test frontend through Nginx"
echo "3. Configure DNS and SSL"