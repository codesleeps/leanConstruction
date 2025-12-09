#!/bin/bash

# ============================================
# VPS Service Verification Script
# ============================================

echo "🔍 Verifying VPS Services Deployment"
echo "====================================="

# Check if running on the VPS
if [[ $(hostname) != *"srv1187860"* ]]; then
    echo "⚠️  Warning: Not running on the expected VPS (srv1187860.hstgr.cloud)"
    echo "This script should be run on the VPS after deployment."
    echo ""
fi

echo "1. Checking system status..."
echo "   Hostname: $(hostname)"
echo "   OS: $(lsb_release -d | cut -f2)"
echo "   Uptime: $(uptime -p)"
echo ""

echo "2. Checking Docker services..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker is installed"
    RUNNING_CONTAINERS=$(docker ps -q | wc -l)
    echo "   📦 Running containers: $RUNNING_CONTAINERS"
else
    echo "   ❌ Docker is not installed"
fi
echo ""

echo "3. Checking PM2 processes..."
if command -v pm2 &> /dev/null; then
    echo "   ✅ PM2 is installed"
    PM2_STATUS=$(pm2 list | grep -c "online")
    if [ $PM2_STATUS -gt 0 ]; then
        echo "   🚀 PM2 processes are running"
        pm2 list
    else
        echo "   ⚠️  No PM2 processes are currently running"
    fi
else
    echo "   ❌ PM2 is not installed"
fi
echo ""

echo "4. Checking Nginx status..."
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
else
    echo "   ❌ Nginx is not running"
fi
echo ""

echo "5. Checking firewall status..."
if ufw status | grep -q "Status: active"; then
    echo "   ✅ Firewall is active"
else
    echo "   ⚠️  Firewall is not active"
fi
echo ""

echo "6. Checking disk space..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "   ✅ Disk usage is healthy: ${DISK_USAGE}%"
else
    echo "   ⚠️  Disk usage is high: ${DISK_USAGE}%"
fi
echo ""

echo "7. Checking memory usage..."
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEM_USAGE < 80" | bc -l) )); then
    echo "   ✅ Memory usage is healthy: ${MEM_USAGE}%"
else
    echo "   ⚠️  Memory usage is high: ${MEM_USAGE}%"
fi
echo ""

echo "8. Checking application directories..."
if [ -d "/var/www/lean-construction" ]; then
    echo "   ✅ Lean Construction AI directory exists"
else
    echo "   ❌ Lean Construction AI directory not found"
fi

if [ -d "/var/www/pixelcraft-bloom" ]; then
    echo "   ✅ PixelCraft Bloom directory exists"
else
    echo "   ❌ PixelCraft Bloom directory not found"
fi
echo ""

echo "✅ Service verification complete!"
echo ""
echo "📋 Next steps:"
echo "1. Ensure DNS records point to your VPS"
echo "2. Set up SSL certificates with Let's Encrypt"
echo "3. Test application access through web browser"
echo "4. Monitor logs with 'pm2 logs' and 'journalctl -u nginx'"