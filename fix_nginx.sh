#!/bin/bash
# Nginx Repair Script
# Usage: ./fix_nginx.sh

VPS_HOST="srv1187860.hstgr.cloud"
DOMAIN="leanaiconstruction.com"

echo "Reparing Nginx Configuration..."

# 1. Create correct Port 80 config locally
cat > nginx_base.conf <<EOF
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
        alias /var/www/lean-ai-construction/frontend;
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

# 2. Upload it
echo "Uploading config..."
scp nginx_base.conf root@$VPS_HOST:/etc/nginx/sites-available/$DOMAIN

# 3. Apply via SSH
echo "Applying config and updating SSL..."
ssh root@$VPS_HOST << 'ENDSSH'
    # Link it
    ln -sf /etc/nginx/sites-available/leanaiconstruction.com /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Config
    nginx -t
    
    # Reload to apply Port 80 changes
    systemctl reload nginx
    
    # Run Certbot to reinstall SSL block based on new Port 80 config
    # This detects the new locations (/api, /dashboard) and adds them to HTTPS block
    echo "Running Certbot..."
    certbot --nginx -d leanaiconstruction.com -d www.leanaiconstruction.com --reinstall --redirect --non-interactive --agree-tos -m admin@leanaiconstruction.com
    
    echo "Nginx Fixed!"
ENDSSH

rm nginx_base.conf
