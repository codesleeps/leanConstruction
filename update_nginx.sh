#!/bin/bash

# Backup current config
cp /etc/nginx/sites-available/leanaiconstruction.com /etc/nginx/sites-available/leanaiconstruction.com.backup

# Check if API proxy already exists
if grep -q "location /api/v1/" /etc/nginx/sites-available/leanaiconstruction.com; then
    echo "API proxy already configured"
    exit 0
fi

# Add API proxy configuration after server_name line
sed -i '/server_name leanaiconstruction.com www.leanaiconstruction.com;/a\
\
    # API Backend Proxy\
    location /api/v1/ {\
        proxy_pass http://localhost:8000;\
        proxy_http_version 1.1;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
    }' /etc/nginx/sites-available/leanaiconstruction.com

# Test configuration
nginx -t

# If test passes, reload
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "Nginx reloaded successfully"
else
    echo "Nginx configuration test failed"
    # Restore backup
    cp /etc/nginx/sites-available/leanaiconstruction.com.backup /etc/nginx/sites-available/leanaiconstruction.com
    exit 1
fi
