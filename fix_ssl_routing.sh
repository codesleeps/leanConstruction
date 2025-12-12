#!/bin/bash
# Nginx SSL Routing Fix Script
# Usage: ./fix_ssl_routing.sh

VPS_HOST="srv1187860.hstgr.cloud"
DOMAIN="leanaiconstruction.com"

echo "Creating Strict Nginx SSL Configuration..."

# Create a robust Nginx config with explicit SSL and Routing
cat > nginx_full.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Backend API - Explicit Proxy
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

# Upload
echo "Uploading config..."
scp nginx_full.conf root@$VPS_HOST:/etc/nginx/sites-available/$DOMAIN

# Apply
echo "Applying config..."
ssh root@$VPS_HOST << 'ENDSSH'
    # Ensure symlink
    ln -sf /etc/nginx/sites-available/leanaiconstruction.com /etc/nginx/sites-enabled/
    
    # Test
    nginx -t
    
    if [ \$? -eq 0 ]; then
        systemctl reload nginx
        echo "✅ Nginx Fixed & Reloaded Successfully!"
    else
        echo "❌ Nginx Config Test Failed! Checking logs..."
        nginx -t
    fi
ENDSSH

rm nginx_full.conf
