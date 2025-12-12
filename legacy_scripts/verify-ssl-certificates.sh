#!/bin/bash

# ============================================
# SSL Certificate Verification Script
# ============================================

echo "🔍 Verifying SSL Certificate Installation"
echo "======================================="

DOMAINS=("constructionaipro.com" "www.constructionaipro.com" "agentsflowai.cloud" "www.agentsflowai.cloud")

for domain in "${DOMAINS[@]}"; do
    echo "➤ Checking SSL certificate for $domain..."
    
    # Check if the domain is accessible via HTTPS
    if command -v curl &> /dev/null; then
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$domain)
        if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 301 ] || [ "$HTTP_STATUS" -eq 302 ]; then
            echo "  ✅ HTTPS is working for $domain (Status: $HTTP_STATUS)"
            
            # Check certificate details
            CERT_INFO=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo "  📅 Certificate details:"
                echo "     $CERT_INFO"
            else
                echo "  ⚠️  Could not retrieve certificate details"
            fi
        else
            echo "  ❌ HTTPS is not working for $domain (Status: $HTTP_STATUS)"
        fi
    else
        echo "  ⚠️  curl is not available for testing"
    fi
    echo ""
done

echo "📋 SSL Certificate Verification Complete"
echo ""
echo "💡 Tips:"
echo "  - Certificates are automatically renewed by Certbot"
echo "  - Check renewal with: sudo certbot renew --dry-run"
echo "  - View certificates with: sudo certbot certificates"