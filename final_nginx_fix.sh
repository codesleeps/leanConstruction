#!/bin/bash
# Final Nginx Fix - Switching to ROOT directive
VPS_HOST="srv1187860.hstgr.cloud"
DOMAIN="leanaiconstruction.com"

echo "Applying Robust Nginx Config..."

cat > nginx_final.conf <<EOF
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

    # FORCE STATIC LOGOS - Using ROOT (Standard)
    # URL: /integrated_tools_logo/xxx
    # File: /var/www/lean-ai-construction/website/public/integrated_tools_logo/xxx
    location /integrated_tools_logo/ {
        root /var/www/lean-ai-construction/website/public;
        try_files \$uri \$uri/ =404;
        access_log off;
        expires max;
    }

    # IMPORTANT: Also serve other public assets if needed (fallback)
    # But specifically target the logos for safety.

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Frontend Dashboard
    location /dashboard {
        alias /var/www/lean-ai-construction/frontend;
        try_files \$uri \$uri/ /dashboard/index.html;
    }

    # Website (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "Uploading..."
scp nginx_final.conf root@$VPS_HOST:/etc/nginx/sites-available/$DOMAIN

echo "Activating..."
ssh root@$VPS_HOST << 'ENDSSH'
    # Ensure Symlink is correct
    ln -sf /etc/nginx/sites-available/leanaiconstruction.com /etc/nginx/sites-enabled/leanaiconstruction.com
    
    # Check for competing configs
    ls -l /etc/nginx/sites-enabled/
    
    # Test and Reload
    nginx -t
    systemctl restart nginx
    
    echo "Nginx Restarted."
    
    # Local Test on VPS to verify Nginx is serving it (headers check)
    echo "Testing locally on VPS..."
    curl -I http://localhost/integrated_tools_logo/procore.webp
ENDSSH

rm nginx_final.conf
