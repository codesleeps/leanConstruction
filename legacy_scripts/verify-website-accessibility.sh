#!/bin/bash

# ============================================
# Website Accessibility Verification Script
# ============================================

echo "🌐 Verifying Website Accessibility"
echo "=============================="

# Define domains
DOMAINS=("constructionaipro.com" "www.constructionaipro.com" "agentsflowai.cloud" "www.agentsflowai.cloud")

echo "🔍 Testing DNS Resolution..."
echo "------------------------"
for domain in "${DOMAINS[@]}"; do
    echo "Checking $domain:"
    IP=$(dig +short $domain 2>/dev/null)
    if [ -n "$IP" ]; then
        echo "  ✅ Resolves to: $IP"
    else
        echo "  ❌ Does not resolve"
    fi
    echo ""
done

echo "🔒 Testing HTTPS Access..."
echo "----------------------"
for domain in "${DOMAINS[@]}"; do
    echo "Testing https://$domain:"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://$domain 2>/dev/null)
    if [ "$RESPONSE" -eq 200 ]; then
        echo "  ✅ HTTPS 200 OK"
    elif [ "$RESPONSE" -eq 301 ] || [ "$RESPONSE" -eq 302 ]; then
        echo "  ➤ HTTPS $RESPONSE (Redirect)"
    else
        echo "  ❌ HTTPS $RESPONSE"
    fi
    echo ""
done

echo "📜 Testing SSL Certificate Validity..."
echo "----------------------------------"
for domain in "${DOMAINS[@]}"; do
    echo "Checking SSL certificate for $domain:"
    CERT_INFO=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "  ✅ Certificate is valid"
        echo "     $CERT_INFO"
    else
        echo "  ❌ Certificate issue or not installed"
    fi
    echo ""
done

echo "📋 Website Accessibility Verification Complete"
echo "========================================="
echo ""
echo "💡 Next Steps:"
echo "  If all tests pass:"
echo "    1. Your websites are successfully deployed and accessible"
echo "    2. Continue with Phase 8 optimization tasks"
echo "  If tests fail:"
echo "    1. Check DNS propagation status at whatsmydns.net"
echo "    2. Verify SSL certificate installation"
echo "    3. Check Nginx configuration and service status"