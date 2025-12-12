#!/bin/bash
VPS_HOST="srv1187860.hstgr.cloud"
REMOTE_DIR="/var/www/lean-ai-construction/website/public"

echo "Syncing Logos to VPS..."
# Recursively copy the folder
scp -r website/public/integrated_tools_logo root@$VPS_HOST:$REMOTE_DIR/

echo "Fixing Permissions..."
ssh root@$VPS_HOST "chmod -R 755 $REMOTE_DIR/integrated_tools_logo"

echo "Restarting Website..."
ssh root@$VPS_HOST "systemctl restart lean-website"

echo "Logos Uploaded & Site Restarted!"
