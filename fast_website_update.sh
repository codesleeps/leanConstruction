#!/bin/bash
# Fast update for Website only
VPS_HOST="srv1187860.hstgr.cloud"
APP_DIR="/var/www/lean-ai-construction"

echo "Building Website locally..."
cd website
# Standard build
npm run build
cd ..

echo "Packaging Website..."
# We only need .next, public, package.json
# Exclude cache to speed up upload
tar -czf website_update.tar.gz --exclude='.next/cache' website/.next website/public website/package.json website/next.config.mjs

echo "Uploading Update..."
scp website_update.tar.gz root@$VPS_HOST:$APP_DIR/

echo "Applying Update on VPS..."
ssh root@$VPS_HOST << 'ENDSSH'
    APP_DIR="/var/www/lean-ai-construction"
    cd $APP_DIR
    
    # Backup current public to be safe (preserve logos if they are there)
    # Actually, tar will overwrite. We want to overwrite code but KEEP logos if they are not in the tar?
    # Our local tar HAS the logos in public/integrated_tools_logo.
    
    tar -xzf website_update.tar.gz
    
    echo "Restarting Website Service..."
    systemctl restart lean-website
    
    echo "Website Updated!"
ENDSSH

rm website_update.tar.gz
