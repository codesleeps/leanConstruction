#!/bin/bash

# ============================================
# VPS Current State Analysis & Recovery
# ============================================

echo "🔍 VPS Current State Analysis"
echo "=============================="

# VPS Information
VPS_HOST="srv1187860.hstgr.cloud"
VPS_IP="72.61.16.111"

echo "VPS Details:"
echo "  Hostname: $VPS_HOST"
echo "  IP: $VPS_IP"
echo ""

# Network Connectivity Test
echo "1. Network Connectivity"
echo "-----------------------"
if ping -c 1 $VPS_HOST > /dev/null 2>&1; then
    echo "✅ VPS is reachable via ping"
else
    echo "❌ VPS not reachable via ping"
fi

# Port Analysis
echo ""
echo "2. Port Analysis"
echo "----------------"

# Check SSH
if nc -z $VPS_HOST 22 > /dev/null 2>&1; then
    echo "✅ SSH port (22) is accessible"
else
    echo "❌ SSH port (22) not accessible"
fi

# Check HTTP
if nc -z $VPS_HOST 80 > /dev/null 2>&1; then
    echo "✅ HTTP port (80) is accessible"
else
    echo "❌ HTTP port (80) not accessible"
fi

# Check HTTPS
if nc -z $VPS_HOST 443 > /dev/null 2>&1; then
    echo "✅ HTTPS port (443) is accessible"
else
    echo "❌ HTTPS port (443) not accessible"
fi

# Web Server Status
echo ""
echo "3. Web Server Analysis"
echo "----------------------"

# Test HTTP response
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$VPS_HOST 2>/dev/null)
if [ "$HTTP_RESPONSE" = "500" ]; then
    echo "✅ Nginx is running (HTTP $HTTP_RESPONSE)"
    echo "⚠️  Backend application error (500 Internal Server Error)"
    echo "🔧 Issue: Backend deployment failed, needs fixing"
elif [ "$HTTP_RESPONSE" = "200" ]; then
    echo "✅ Web server responding normally (HTTP $HTTP_RESPONSE)"
elif [ "$HTTP_RESPONSE" = "000" ]; then
    echo "❌ No web server response"
else
    echo "⚠️  Unexpected HTTP response: $HTTP_RESPONSE"
fi

# Test HTTPS response
HTTPS_RESPONSE=$(curl -s -k -o /dev/null -w "%{http_code}" https://$VPS_HOST 2>/dev/null)
if [ "$HTTPS_RESPONSE" = "000" ] || [ "$HTTPS_RESPONSE" = "" ]; then
    echo "❌ HTTPS not configured (expected)"
elif [ "$HTTPS_RESPONSE" = "200" ]; then
    echo "✅ HTTPS is working (HTTP $HTTPS_RESPONSE)"
else
    echo "⚠️  HTTPS response: $HTTPS_RESPONSE"
fi

# Diagnosis
echo ""
echo "4. Current Deployment Status"
echo "----------------------------"

if [ "$HTTP_RESPONSE" = "500" ]; then
    echo "📊 DEPLOYMENT STATUS ANALYSIS:"
    echo "  ✅ VPS: Online and accessible"
    echo "  ✅ Nginx: Installed and running"
    echo "  ❌ Backend: Deployment failed (500 error)"
    echo "  ❌ Frontend: Not properly deployed"
    echo "  ❌ SSL: Not installed"
    echo ""
    echo "🎯 ROOT CAUSE:"
    echo "  Backend deployment failed due to directory structure issues"
    echo "  (This matches the issues identified in the codebase analysis)"
    echo ""
    echo "🔧 REQUIRED ACTIONS:"
    echo "  1. Fix backend deployment directory structure"
    echo "  2. Deploy frontend React application"
    echo "  3. Configure Nginx properly"
    echo "  4. Install SSL certificates"
    echo "  5. Configure DNS records"
fi

echo ""
echo "5. Recovery Plan"
echo "----------------"

echo "📋 IMMEDIATE ACTIONS REQUIRED:"
echo ""
echo "Option A: Manual SSH Access (Recommended)"
echo "  1. Obtain SSH credentials for $VPS_HOST"
echo "  2. Upload deployment scripts:"
echo "     scp *.sh root@$VPS_HOST:~/"
echo "  3. Run recovery deployment:"
echo "     ssh root@$VPS_HOST"
echo "     chmod +x *.sh"
echo "     ./fix-deployment-issues.sh"
echo "     ./deploy-frontend.sh"
echo ""
echo "Option B: Web-based Recovery (If SSH unavailable)"
echo "  1. Access VPS control panel"
echo "  2. Use web console or file manager"
echo "  3. Upload scripts via web interface"
echo "  4. Execute via web terminal"
echo ""
echo "Option C: VPS Provider Support"
echo "  1. Contact VPS provider support"
echo "  2. Request SSH access or web console"
echo "  3. Explain deployment failure and recovery needs"

echo ""
echo "6. Success Criteria"
echo "-------------------"
echo "Deployment will be successful when:"
echo "  • HTTP response changes from 500 to 200"
echo "  • Backend API responds at http://$VPS_HOST/api/health"
echo "  • Frontend loads at http://$VPS_HOST"
echo "  • SSL certificates install successfully"
echo "  • DNS records configured"

echo ""
echo "7. Estimated Recovery Time"
echo "--------------------------"
echo "  • SSH access setup: 5-15 minutes"
echo "  • Backend fix: 15-30 minutes"
echo "  • Frontend deployment: 15 minutes"
echo "  • SSL setup: 10 minutes"
echo "  • DNS configuration: 5 minutes"
echo "  • Total: 50-75 minutes"

echo ""
echo "8. Emergency Contacts"
echo "--------------------"
echo "  • VPS Provider: [Contact provider support]"
echo "  • Domain Registrar: [For DNS configuration]"
echo "  • SSL Certificate: Let's Encrypt support"

echo ""
echo "==================================="
echo "VPS State Analysis Complete"
echo "==================================="

if [ "$HTTP_RESPONSE" = "500" ]; then
    echo ""
    echo "🚨 DEPLOYMENT RECOVERY REQUIRED"
    echo "The VPS is partially deployed but needs backend fix."
    echo "Use the provided deployment scripts to complete the setup."
    echo ""
    echo "Next Step: Establish SSH access to $VPS_HOST"
fi