#!/bin/bash

echo "🎯 Manual Deployment Completion"
echo "==============================="

# Configuration
DOMAIN_LEAN="constructionaipro.com"
DOMAIN_PIXEL="agentsflowai.cloud"
EMAIL="codesleep43@gmail.com"

# Kill the old deployment process
echo "🛑 Stopping old deployment process..."
pkill -f vps-deployment.sh 2>/dev/null || true

# Clean and extract applications
echo "📦 Extracting applications..."
cd /var/www/lean-construction

# Remove any existing content
rm -rf * .* 2>/dev/null || true

# Extract backend application
echo "Extracting backend..."
tar -xzf /tmp/lean-construction-backend.tar.gz

# Set permissions
chown -R root:root /var/www/lean-construction
chmod -R 755 /var/www/lean-construction

echo "✅ Backend extracted"

# Deploy backend
echo "🐍 Setting up Python backend..."
cd /var/www/lean-construction

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn[standard] gunicorn

# Install additional requirements if they exist
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "✅ Backend Python environment ready"

# Deploy frontend
echo "⚛️  Setting up React frontend..."
cd /var/www/lean-construction

# If frontend directory exists, build it
if [ -d "frontend" ]; then
    cd frontend
    
    # Install Node.js dependencies
    npm install
    
    # Build for production
    npm run build
    
    echo "✅ Frontend built"
else
    echo "⚠️  Frontend directory not found, creating placeholder..."
    mkdir -p build
    echo '<!DOCTYPE html><html><head><title>Lean Construction AI</title></head><body><h1>Construction AI - Coming Soon</h1></body></html>' > build/index.html
fi

# Configure Nginx for Lean Construction AI
echo "🌐 Configuring Nginx for Lean Construction AI..."
cat > /etc/nginx/sites-available/lean-construction << EOF
server {
    listen 80;
    server_name $DOMAIN_LEAN www.$DOMAIN_LEAN;
    
    root /var/www/lean-construction/frontend/build;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location / {
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Create placeholder for PixelCraft Bloom
echo "🎮 Creating PixelCraft Bloom placeholder..."
mkdir -p /var/www/pixelcraft-bloom
cat > /var/www/pixelcraft-bloom/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelCraft Bloom</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 3em; margin-bottom: 20px; }
        p { font-size: 1.2em; margin: 20px 0; }
        .status { background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 PixelCraft Bloom</h1>
        <div class="status">
            <h2>🌟 Coming Soon!</h2>
            <p>Creative design application by CodeSleeps</p>
            <p>AI-powered pixel art generation and creative tools</p>
        </div>
        <p>📧 Contact: codesleeps@gmail.com</p>
        <p>🌐 Domain: agentsflowai.cloud</p>
    </div>
</body>
</html>
EOF

# Configure Nginx for PixelCraft Bloom
cat > /etc/nginx/sites-available/pixelcraft-bloom << EOF
server {
    listen 80;
    server_name $DOMAIN_PIXEL www.$DOMAIN_PIXEL;
    
    root /var/www/pixelcraft-bloom;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:; img-src 'self' data: https:;" always;
    
    # Static files
    location / {
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Enable sites
ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/pixelcraft-bloom /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl reload nginx

# Create PM2 configuration for backend
echo "⚙️  Setting up PM2 for backend..."
cd /var/www/lean-construction

cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: 'uvicorn',
    args: 'app.main_lite:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/lean-construction',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production',
      PORT: 8000
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/log/lean-construction/pm2-error.log',
    out_file: '/var/log/lean-construction/pm2-out.log',
    log_file: '/var/log/lean-construction/pm2-combined.log',
    time: true
  }]
};
EOF

# Start backend with PM2
echo "🚀 Starting backend services..."
source venv/bin/activate
pm2 start ecosystem.config.js
pm2 save

# Enable PM2 startup
pm2 startup || true

# Setup SSL certificates (commented for now)
echo "🔒 SSL certificates can be set up later with:"
echo "certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN"
echo "certbot --nginx -d $DOMAIN_PIXEL -d www.$DOMAIN_PIXEL"

# Create monitoring script
echo "📊 Setting up monitoring..."
cat > /usr/local/bin/app-monitor.sh << 'EOF'
#!/bin/bash

# Check if PM2 processes are running
if ! pm2 list | grep -q "online"; then
    echo "PM2 processes not running, restarting..."
    pm2 restart all
fi

# Check Nginx
if ! systemctl is-active --quiet nginx; then
    echo "Nginx not running, restarting..."
    sudo systemctl restart nginx
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "Disk usage is ${DISK_USAGE}%, consider cleanup"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "Memory usage is ${MEM_USAGE}%, check processes"
fi
EOF

chmod +x /usr/local/bin/app-monitor.sh

# Add monitoring to cron
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh >> /var/log/app-monitor.log 2>&1") | crontab -

echo ""
echo "✅ Deployment Complete!"
echo "=================================================="
echo "🎉 Both applications deployed successfully!"
echo ""
echo "🌐 Current URLs (HTTP):"
echo "   Lean Construction AI: http://$DOMAIN_LEAN"
echo "   PixelCraft Bloom: http://$DOMAIN_PIXEL"
echo ""
echo "📊 Service Status:"
echo "   Backend API: Check with 'pm2 status'"
echo "   Nginx: Check with 'systemctl status nginx'"
echo "   Logs: pm2 logs lean-construction-api"
echo ""
echo "🔒 Next Steps:"
echo "1. Update DNS records to point to this VPS IP"
echo "2. Set up SSL certificates with certbot"
echo "3. Test all functionality"
echo ""
echo "=================================================="