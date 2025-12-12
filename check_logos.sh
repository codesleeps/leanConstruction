#!/bin/bash
# Check remote files
VPS_HOST="srv1187860.hstgr.cloud"
TARGET_DIR="/var/www/lean-ai-construction/website/public/integrated_tools_logo"

echo "Checking remote directory: $TARGET_DIR"
ssh root@$VPS_HOST "ls -F $TARGET_DIR"
