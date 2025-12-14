#!/bin/bash

# Script to finish backend deployment on VPS
# Run this ON THE VPS: ssh root@srv1187860.hstgr.cloud
# Then: bash /var/www/lean-ai-construction/backend/finish_backend_deployment.sh

set -e

echo "=== Finishing Backend Deployment ==="
echo ""

cd /var/www/lean-ai-construction/backend

# Comment out ML-related imports in main.py if not already done
echo "Commenting out ML imports..."
sed -i 's/^from .api.ml_routes import/# from .api.ml_routes import/g' app/main.py
sed -i 's/^    app.include_router(ml_router)/    # app.include_router(ml_router)/g' app/main.py

# Also comment out the ML import in api/__init__.py if it exists
if [ -f "app/api/__init__.py" ]; then
    sed -i 's/^from .ml_routes import/# from .ml_routes import/g' app/api/__init__.py
    sed -i 's/^    ml_router/    # ml_router/g' app/api/__init__.py
fi

echo "ML imports commented out successfully"
echo ""

# Restart the backend service
echo "Restarting backend service..."
systemctl restart lean-backend

# Wait a moment for service to start
sleep 3

# Check status
echo ""
echo "=== Backend Service Status ==="
systemctl status lean-backend --no-pager -l

echo ""
echo "=== Recent Backend Logs ==="
journalctl -u lean-backend -n 20 --no-pager

echo ""
echo "=== Deployment Complete ==="
echo "Website: https://leanaiconstruction.com"
echo "API: https://leanaiconstruction.com/api"
echo "API Docs: https://leanaiconstruction.com/docs"
