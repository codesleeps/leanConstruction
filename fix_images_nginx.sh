#!/bin/bash
# Force Nginx to serve logos directly
VPS_HOST="srv1187860.hstgr.cloud"
DOMAIN="leanaiconstruction.com"

echo "Configuring Nginx to serve images directly..."

cat > nginx_static_fix.conf <<EOF
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

    # FORCE STATIC LOGOS - Direct Nginx Serving
    location /integrated_tools_logo/ {
        alias /var/www/lean-ai-construction/website/public/integrated_tools_logo/;
        try_files \$uri \$uri/ =404;
        access_log off;
        expires max;
    }

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

    # Website (Next.js) - Default fallback
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "Uploading Config..."
scp nginx_static_fix.conf root@$VPS_HOST:/etc/nginx/sites-available/$DOMAIN

echo "Applying & Reloading..."
ssh root@$VPS_HOST << 'ENDSSH'
    # Config is already linked, just check and reload
    nginx -t
    systemctl reload nginx
    echo "Nginx Updated."
    
    # Verify files exist on disk
    echo "Verifying file existence on disk:"
    ls -F /var/www/lean-ai-construction/website/public/integrated_tools_logo/
ENDSSH

rm nginx_static_fix.conf
