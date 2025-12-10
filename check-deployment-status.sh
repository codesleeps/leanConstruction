#!/bin/bash

# ============================================
# Production Deployment Status Check
# ============================================

echo "🔍 Production Deployment Status Check"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service_name=$1
    local check_command=$2
    
    echo -n "Checking $service_name... "
    if eval $check_command > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not Running${NC}"
        return 1
    fi
}

# Function to check port
check_port() {
    local port=$1
    local service_name=$2
    
    echo -n "Checking port $port ($service_name)... "
    if netstat -ln 2>/dev/null | grep -q ":$port " || ss -ln 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✅ Open${NC}"
        return 0
    else
        echo -e "${RED}❌ Closed${NC}"
        return 1
    fi
}

echo ""
echo "1. System Services"
echo "-------------------"

# Check PM2
check_service "PM2 Process Manager" "pm2 list"

# Check Nginx
check_service "Nginx Web Server" "sudo systemctl is-active nginx"

# Check system resources
echo ""
echo "2. System Resources"
echo "-------------------"

# CPU and Memory
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print "  Usage: " $1 "%"}'

echo "Memory Usage:"
free -h | awk '/^Mem:/ {printf "  Used: %s / %s (%.1f%%)\n", $3,$2,$3*100/$2 }'

# Disk usage
echo "Disk Usage:"
df -h / | awk 'NR==2 {printf "  Used: %s / %s (%s)\n", $3,$2,$5}'

echo ""
echo "3. Network Ports"
echo "----------------"

# Check important ports
check_port 80 "HTTP"
check_port 443 "HTTPS"
check_port 8000 "Backend API"
check_port 3000 "Frontend Dev" || true
check_port 5555 "Flower Monitor" || true

echo ""
echo "4. Application Status"
echo "---------------------"

# Check backend API
echo -n "Backend API Health... "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Responding${NC}"
    
    # Get API info
    API_VERSION=$(curl -s http://localhost:8000/health | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")
    echo "  Version: $API_VERSION"
else
    echo -e "${RED}❌ Not Responding${NC}"
fi

# Check frontend
echo -n "Frontend Build... "
if [ -d "/var/www/lean-construction/frontend/build" ] && [ -f "/var/www/lean-construction/frontend/build/index.html" ]; then
    echo -e "${GREEN}✅ Built${NC}"
    BUILD_SIZE=$(du -sh /var/www/lean-construction/frontend/build 2>/dev/null | cut -f1 || echo "unknown")
    echo "  Size: $BUILD_SIZE"
else
    echo -e "${RED}❌ Not Built${NC}"
fi

echo ""
echo "5. PM2 Processes"
echo "----------------"

if command -v pm2 > /dev/null 2>&1; then
    pm2 list 2>/dev/null || echo "No PM2 processes running"
else
    echo -e "${RED}PM2 not installed${NC}"
fi

echo ""
echo "6. File Permissions"
echo "-------------------"

# Check critical directories
for dir in "/var/www/lean-construction" "/var/www/lean-construction/frontend/build"; do
    if [ -d "$dir" ]; then
        echo -n "Directory $dir... "
        if [ -w "$dir" ]; then
            echo -e "${GREEN}✅ Writable${NC}"
        else
            echo -e "${YELLOW}⚠️  Not Writable${NC}"
        fi
    fi
done

echo ""
echo "7. Environment Configuration"
echo "----------------------------"

# Check environment files
if [ -f "/var/www/lean-construction/.env" ]; then
    echo -e "${GREEN}✅ Backend .env exists${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env missing${NC}"
fi

if [ -f "/var/www/lean-construction/frontend/.env.production" ]; then
    echo -e "${GREEN}✅ Frontend .env.production exists${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend .env.production missing${NC}"
fi

echo ""
echo "8. Recent Logs"
echo "--------------"

# Check recent errors
if [ -f "/var/www/lean-construction/logs/pm2-error.log" ]; then
    ERROR_COUNT=$(tail -50 /var/www/lean-construction/logs/pm2-error.log 2>/dev/null | grep -c "ERROR" || echo "0")
    echo "Recent PM2 errors: $ERROR_COUNT"
fi

echo ""
echo "9. Next Steps Required"
echo "----------------------"

# Determine what needs to be done
NEEDS_BACKEND=false
NEEDS_FRONTEND=false
NEEDS_DNS=false
NEEDS_SSL=false

# Check backend
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    NEEDS_BACKEND=true
fi

# Check frontend
if [ ! -d "/var/www/lean-construction/frontend/build" ] || [ ! -f "/var/www/lean-construction/frontend/build/index.html" ]; then
    NEEDS_FRONTEND=true
fi

# Check DNS (basic check)
if ! nslookup constructionaipro.com > /dev/null 2>&1; then
    NEEDS_DNS=true
fi

# Check SSL
if ! openssl s_client -connect constructionaipro.com:443 -servername constructionaipro.com </dev/null 2>/dev/null | grep -q "Verify return code"; then
    NEEDS_SSL=true
fi

if [ "$NEEDS_BACKEND" = true ]; then
    echo -e "${RED}❌ Backend deployment needed${NC} - Run: ./fix-deployment-issues.sh"
fi

if [ "$NEEDS_FRONTEND" = true ]; then
    echo -e "${YELLOW}⚠️  Frontend deployment needed${NC} - Run: ./deploy-frontend.sh"
fi

if [ "$NEEDS_DNS" = true ]; then
    echo -e "${YELLOW}⚠️  DNS configuration needed${NC} - Point domains to VPS IP"
fi

if [ "$NEEDS_SSL" = true ]; then
    echo -e "${YELLOW}⚠️  SSL certificates needed${NC} - Run: sudo certbot --nginx -d constructionaipro.com"
fi

if [ "$NEEDS_BACKEND" = false ] && [ "$NEEDS_FRONTEND" = false ] && [ "$NEEDS_DNS" = false ] && [ "$NEEDS_SSL" = false ]; then
    echo -e "${GREEN}✅ All basic deployment tasks completed!${NC}"
    echo "Ready for final testing and go-live."
fi

echo ""
echo "======================================"
echo "Status check completed!"
echo "======================================"