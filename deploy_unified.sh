#!/bin/bash

# Load NVM if present to ensure node/npm are available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check definitions
VPS_USER="root"
VPS_HOST="srv1187860.hstgr.cloud"
APP_DIR="/var/www/lean-ai-construction"
DOMAIN="leanaiconstruction.com"

echo "========================================================"
echo "   Lean AI Construction - Production Deployment"
echo "   (Standard Deployment Mode)"
echo "========================================================"
echo "Target VPS: $VPS_HOST"
echo "Target Domain: $DOMAIN"
echo ""

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "Error: npm could not be found. Please ensure Node.js is installed and in your PATH."
    exit 1
fi

# 1. Build Frontend Dashboard (React)
echo "--------------------------------------------------------"
echo "Step 1: Building Dashboard (React App)..."
echo "--------------------------------------------------------"
cd frontend
if [ ! -d "node_modules" ]; then
    npm ci
fi
npm run build
cd ..

# 2. Build Website (Next.js)
echo "--------------------------------------------------------"
echo "Step 2: Building Website (Next.js)..."
echo "--------------------------------------------------------"
cd website
if [ ! -d "node_modules" ]; then
    npm ci
fi
# Standard build (not standalone)
npm run build
cd ..

# 3. Prepare Deployment Package
echo "--------------------------------------------------------"
echo "Step 3: Packaging Applications..."
echo "--------------------------------------------------------"
mkdir -p dist

tar -czf dist/deploy_package.tar.gz \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='legacy_scripts' \
    backend \
    website/.next \
    website/public \
    website/package.json \
    website/package-lock.json \
    website/next.config.mjs \
    frontend/build \
    docker-compose.yml \
    Dockerfile
    
echo "Package created at dist/deploy_package.tar.gz"

# 4. Create Remote Directory Structure
echo "--------------------------------------------------------"
echo "Step 4: Setting up Remote Server..."
echo "--------------------------------------------------------"
ssh $VPS_USER@$VPS_HOST "mkdir -p $APP_DIR/backend $APP_DIR/website $APP_DIR/frontend $APP_DIR/nginx"

# 5. Generate Nginx Configuration (Unified)
echo "Generating Nginx Config..."
cat > dist/nginx.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Docs shortcut
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    # Frontend Dashboard (Serve React Static)
    location /dashboard {
        alias $APP_DIR/frontend;
        try_files \$uri \$uri/ /dashboard/index.html;
    }

    # Website (Next.js Standard)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 6. Upload Files
echo "--------------------------------------------------------"
echo "Step 6: Uploading Files..."
echo "--------------------------------------------------------"
scp dist/deploy_package.tar.gz $VPS_USER@$VPS_HOST:$APP_DIR/
scp dist/nginx.conf $VPS_USER@$VPS_HOST:/etc/nginx/sites-available/$DOMAIN

# 7. Extract and Install on VPS
echo "--------------------------------------------------------"
echo "Step 7: Installing on VPS..."
echo "--------------------------------------------------------"
ssh $VPS_USER@$VPS_HOST "cd $APP_DIR && tar -xzf deploy_package.tar.gz"

echo "Running Remote Setup Script..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
    set -e
    APP_DIR="/var/www/lean-ai-construction"
    
    # 1. Install Website Dependencies
    echo "Installing Website Dependencies..."
    cd $APP_DIR/website
    npm install --production

    # 2. Setup Backend
    echo "Setting up Backend..."
    cd $APP_DIR/backend
    # Install Python 3.10 or ensure venv
    if ! command -v python3 &> /dev/null; then
        apt-get update && apt-get install -y python3-venv python3-pip
    fi
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 3. Setup Systemd Service for Backend
    echo "Configuring Backend Service..."
    cat > /etc/systemd/system/lean-backend.service <<EOL
[Unit]
Description=Lean AI Construction Backend
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR/backend
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

    # 4. Setup Systemd Service for Website (Next.js)
    echo "Configuring Website Service..."
    cat > /etc/systemd/system/lean-website.service <<EOL
[Unit]
Description=Lean AI Construction Website
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR/website
Environment=NODE_ENV=production
Environment=PORT=3000
# Use system npm to start next
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

    # 5. Reload Services
    systemctl daemon-reload
    systemctl enable lean-backend
    systemctl enable lean-website
    systemctl restart lean-backend
    systemctl restart lean-website

    # 6. Enable Nginx Site
    ln -sf /etc/nginx/sites-available/leanaiconstruction.com /etc/nginx/sites-enabled/
    # Remove default if exists
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t && systemctl restart nginx
    
    echo "Deployment Complete!"
ENDSSH
