#!/bin/bash

# ============================================
# Website Accessibility Diagnostic Script
# ============================================

echo "🔍 Diagnosing Website Accessibility Issues"
echo "======================================"

echo "1. Checking DNS Resolution..."
echo "----------------------------"
for domain in constructionaipro.com www.constructionaipro.com agentsflowai.cloud www.agentsflowai.cloud; do
    echo "Checking $domain:"
    if command -v dig &> /dev/null; then
        IP=$(dig +short $domain)
        if [ -n "$IP" ]; then
            echo "  ✅ Resolves to: $IP"
        else
            echo "  ❌ Does not resolve"
        fi
    else
        echo "  ⚠️  dig command not available"
    fi
    echo ""
done

echo "2. Checking Port Connectivity..."
echo "-----------------------------"
for port in 80 443; do
    echo "Checking port $port:"
    if command -v nc &> /dev/null; then
        if nc -z srv1187860.hstgr.cloud $port 2>/dev/null; then
            echo "  ✅ Port $port is accessible"
        else
            echo "  ❌ Port $port is not accessible"
        fi
    else
        echo "  ⚠️  nc command not available"
    fi
    echo ""
done

echo "3. Checking HTTP Response..."
echo "--------------------------"
for domain in constructionaipro.com agentsflowai.cloud; do
    echo "Checking http://$domain:"
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$domain 2>/dev/null)
        if [ "$RESPONSE" -eq 200 ]; then
            echo "  ✅ HTTP 200 OK"
        elif [ "$RESPONSE" -eq 301 ] || [ "$RESPONSE" -eq 302 ]; then
            echo "  ➤ HTTP $RESPONSE (Redirect)"
        else
            echo "  ❌ HTTP $RESPONSE"
        fi
    else
        echo "  ⚠️  curl command not available"
    fi
    echo ""
done

echo "4. Checking HTTPS Response..."
echo "---------------------------"
for domain in constructionaipro.com agentsflowai.cloud; do
    echo "Checking https://$domain:"
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://$domain 2>/dev/null)
        if [ "$RESPONSE" -eq 200 ]; then
            echo "  ✅ HTTPS 200 OK"
        elif [ "$RESPONSE" -eq 301 ] || [ "$RESPONSE" -eq 302 ]; then
            echo "  ➤ HTTPS $RESPONSE (Redirect)"
        else
            echo "  ❌ HTTPS $RESPONSE"
        fi
    else
        echo "  ⚠️  curl command not available"
    fi
    echo ""
done

echo "5. Checking SSL Certificate Status..."
echo "----------------------------------"
for domain in constructionaipro.com agentsflowai.cloud; do
    echo "Checking SSL certificate for $domain:"
    if command -v openssl &> /dev/null; then
        CERT_INFO=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "  ✅ Certificate is installed and valid"
            echo "     $CERT_INFO"
        else
            echo "  ❌ Certificate issue or not installed"
        fi
    else
        echo "  ⚠️  openssl command not available"
    fi
    echo ""
done

echo "📋 Diagnostic Summary"
echo "=================="
echo "If DNS resolves correctly but websites are not accessible:"
echo "1. Wait for DNS propagation (can take up to 48 hours)"
echo "2. Check if SSL certificates are properly installed"
echo "3. Verify Nginx configuration files"
echo "4. Check firewall settings"
echo "5. Ensure all services are running correctly"