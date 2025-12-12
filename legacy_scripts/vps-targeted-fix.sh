#!/bin/bash

echo "🔧 VPS Targeted Fix - Addressing Specific Issues"
echo "=============================================="

# Connect to VPS and fix issues
ssh -i ~/.ssh/vps_deploy_key root@srv1187860.hstgr.cloud << 'VPSCOMMANDS'

echo "Step 1: Fix PM2 configuration and restart..."
# Stop all PM2 processes
pm2 delete all 2>/dev/null || true

# Kill any existing Python processes on port 8000
pkill -f "python.*8000" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true

# Start the minimal backend directly on port 8000
cd /var/www/lean-construction
source venv/bin/activate
nohup python minimal_backend.py > logs/backend.log 2>&1 &
echo $! > backend.pid
sleep 3

echo "Step 2: Test backend directly..."
# Test if backend is responding
curl -s http://localhost:8000/health && echo "Backend working!" || echo "Backend still not working"

echo "Step 3: Fix Nginx configuration..."
# Fix the rewrite cycle issue by checking nginx config
cat > /etc/nginx/sites-available/lean-construction << 'NGINXCONFIG'
server {
    listen 80;
    server_name srv1187860.hstgr.cloud constructionaipro.com www.constructionaipro.com agentsflowai.cloud www.agentsflowai.cloud;
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Direct backend endpoints
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \$host;
    }
    
    # Frontend (React build)
    location / {
        root /var/www/lean-construction/frontend/build;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Add caching headers
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
NGINXCONFIG

# Test and reload nginx
nginx -t && systemctl reload nginx && echo "✅ Nginx configuration fixed and reloaded" || echo "❌ Nginx configuration failed"

echo "Step 4: Build frontend..."
cd /var/www/lean-construction/frontend
if [ -f "package.json" ]; then
    npm install
    npm run build
    echo "✅ Frontend built"
else
    echo "⚠️ Frontend package.json not found"
fi

echo "Step 5: Set proper permissions..."
chown -R www-data:www-data /var/www/lean-construction/frontend/build
chmod -R 755 /var/www/lean-construction/frontend/build

echo "Step 6: Final verification..."
echo "Backend status:"
ps aux | grep python | grep -v grep

echo "Port 8000 status:"
netstat -tlnp | grep :8000 || echo "Port 8000 not listening"

echo "Nginx status:"
systemctl status nginx --no-pager -l

VPSCOMMANDS

echo "Targeted fix script executed!"
echo "Checking results..."

# Test the fix
sleep 5
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://srv1187860.hstgr.cloud)
echo "HTTP Status after fix: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo "🎉 FIX SUCCESSFUL! HTTP 200!"
else
    echo "Fix applied, status: $HTTP_STATUS"
fi

# Test specific endpoints
echo "Testing specific endpoints:"
echo "Root: $(curl -s -o /dev/null -w "%{http_code}" http://srv1187860.hstgr.cloud/)"
echo "Health: $(curl -s -o /dev/null -w "%{http_code}" http://srv1187860.hstgr.cloud/health)"
echo "API: $(curl -s -o /dev/null -w "%{http_code}" http://srv1187860.hstgr.cloud/api/)"

