#!/bin/bash

# ============================================
# VPS Deployment Script for Both Apps (Modified)
# ============================================
#
# ⚠️  DEPRECATED: This script is deprecated in favor of:
#   - backend/deploy-backend.sh (for backend deployment)
#   - deploy/production-deployment.sh (for full deployment)
#
# This script contains local macOS paths that won't work on VPS.
# Use the modern deployment scripts instead.
# ============================================

set -e

echo "🚀 Starting VPS Deployment for Lean Construction AI + PixelCraft Bloom"
echo "=================================================="

# Check if running as root (allow for VPS deployment)
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Running as root - VPS deployment mode enabled"
   echo "🔒 Security: Ensure you trust the source of this script"
fi

# Configuration
DOMAIN_LEAN="constructionaipro.com"
DOMAIN_PIXEL="agentsflowai.cloud"
EMAIL="codesleep43@gmail.com"
VPS_IP="srv1187860.hstgr.cloud"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt install -y curl wget git unzip nginx certbot python3 python3-pip python3-venv docker.io docker-compose nodejs npm

# Install Node.js 20.x
echo "📦 Installing Node.js 20.x..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 for Node.js process management
echo "📦 Installing PM2..."
sudo npm install -g pm2

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create app directories
echo "📁 Creating app directories..."
sudo mkdir -p /var/www/lean-construction
sudo mkdir -p /var/www/pixelcraft-bloom
sudo mkdir -p /var/log/lean-construction
sudo mkdir -p /var/log/pixelcraft-bloom

# Extract applications from tar.gz files
echo "📤 Extracting applications from tar.gz files..."
cd /var/www/lean-construction
# NOTE: This script expects tarballs at:
#   /tmp/lean-construction-backend.tar.gz
#   /tmp/lean-construction-frontend.tar.gz
# These should be copied to VPS via scp before running this script
sudo tar -xzf /tmp/lean-construction-backend.tar.gz --strip-components=1
sudo tar -xzf /tmp/lean-construction-frontend.tar.gz --strip-components=1

cd /var/www/pixelcraft-bloom
# For PixelCraft Bloom, we'll need to get it from GitHub or another source
# For now, we'll create a basic structure
sudo mkdir -p build

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R $USER:$USER /var/www/lean-construction
sudo chown -R $USER:$USER /var/www/pixelcraft-bloom
sudo chown -R $USER:$USER /var/log/lean-construction
sudo chown -R $USER:$USER /var/log/pixelcraft-bloom

# Deploy Lean Construction AI Backend
echo "🏗️  Deploying Lean Construction AI Backend..."
cd /var/www/lean-construction/backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn[standard] gunicorn

# Deploy Lean Construction AI Frontend
echo "🏗️  Deploying Lean Construction AI Frontend..."
cd /var/www/lean-construction/frontend
npm install
npm run build

# Deploy PixelCraft Bloom
echo "🎮 Deploying PixelCraft Bloom..."
cd /var/www/pixelcraft-bloom
# For now, we'll just create a placeholder
echo "<html><body><h1>PixelCraft Bloom Coming Soon</h1></body></html>" > build/index.html

# Create Nginx configuration for both apps
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/lean-construction > /dev/null <<EOF
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

sudo tee /etc/nginx/sites-available/pixelcraft-bloom > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_PIXEL www.$DOMAIN_PIXEL;
    
    root /var/www/pixelcraft-bloom/build;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:; img-src 'self' data: https:;" always;
    
    # API proxy (if needed)
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
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

# Enable sites
sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/pixelcraft-bloom /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Create PM2 configuration for backend services
echo "⚙️  Creating PM2 configuration..."
cd /var/www/lean-construction/backend

cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: 'uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/lean-construction/backend',
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

# Start Lean Construction AI backend with PM2
echo "🚀 Starting Lean Construction AI backend..."
source venv/bin/activate
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# Create SSL certificates (commented out for initial deployment)
echo "🔒 Setting up SSL certificates..."
# sudo certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN --non-interactive --agree-tos --email $EMAIL
# sudo certbot --nginx -d $DOMAIN_PIXEL -d www.$DOMAIN_PIXEL --non-interactive --agree-tos --email $EMAIL

# Create monitoring script
echo "📊 Creating monitoring script..."
sudo tee /usr/local/bin/app-monitor.sh > /dev/null <<'EOF'
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

sudo chmod +x /usr/local/bin/app-monitor.sh

# Add monitoring to cron (check every 5 minutes)
echo "⏰ Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh >> /var/log/app-monitor.log 2>&1") | crontab -

# Create backup script
echo "💾 Creating backup script..."
sudo tee /usr/local/bin/backup-apps.sh > /dev/null <<'EOF'
#!/bin/bash

BACKUP_DIR="/var/backups/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p $BACKUP_DIR

# Backup app directories
tar -czf $BACKUP_DIR/lean-construction.tar.gz -C /var/www lean-construction
tar -czf $BACKUP_DIR/pixelcraft-bloom.tar.gz -C /var/www pixelcraft-bloom

# Backup logs
tar -czf $BACKUP_DIR/logs.tar.gz -C /var/log lean-construction pixelcraft-bloom

# Keep only last 7 days of backups
find /var/backups -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"
EOF

sudo chmod +x /usr/local/bin/backup-apps.sh

# Add backup to cron (daily at 2 AM)
echo "⏰ Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-apps.sh") | crontab -

# Restart services
echo "🔄 Restarting services..."
sudo systemctl reload nginx

echo ""
echo "✅ Deployment Complete!"
echo "=================================================="
echo "🎉 Both apps deployed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your domain DNS records to point to: $VPS_IP"
echo "2. Run SSL certificate setup:"
echo "   sudo certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN"
echo "   sudo certbot --nginx -d $DOMAIN_PIXEL -d www.$DOMAIN_PIXEL"
echo ""
echo "🔗 URLs (after DNS update):"
echo "   Lean Construction AI: http://$DOMAIN_LEAN"
echo "   PixelCraft Bloom: http://$DOMAIN_PIXEL"
echo ""
echo "📊 Monitoring:"
echo "   PM2 status: pm2 status"
echo "   App logs: pm2 logs"
echo "   Nginx status: sudo systemctl status nginx"
echo "   Monitor script: /usr/local/bin/app-monitor.sh"
echo ""
echo "💾 Backup:"
echo "   Manual backup: sudo /usr/local/bin/backup-apps.sh"
echo "   Automatic backups: Daily at 2 AM"
echo "=================================================="