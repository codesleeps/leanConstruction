#!/bin/bash

# ============================================
# DNS Propagation Checker
# ============================================

echo "🔍 Checking DNS Propagation Status"
echo "================================="

DOMAINS=("constructionaipro.com" "www.constructionaipro.com" "agentsflowai.cloud" "www.agentsflowai.cloud")
TARGET_HOST="srv1187860.hstgr.cloud"

echo "Checking if DNS records point to $TARGET_HOST"
echo ""

for domain in "${DOMAINS[@]}"; do
    echo "➤ Checking $domain..."
    
    # Try to resolve the domain
    if command -v dig &> /dev/null; then
        RESULT=$(dig +short $domain)
    elif command -v nslookup &> /dev/null; then
        RESULT=$(nslookup $domain | grep -A 1 "Name:" | tail -1 | awk '{print $2}')
    else
        echo "  ⚠️  Neither dig nor nslookup is available"
        continue
    fi
    
    if [[ $RESULT == *"$TARGET_HOST"* ]] || [[ $RESULT == "72.61.16.111" ]]; then
        echo "  ✅ $domain correctly points to $TARGET_HOST"
    else
        echo "  ❌ $domain does not point to $TARGET_HOST"
        echo "     Current value: $RESULT"
    fi
    echo ""
done

echo "📋 DNS Propagation Check Complete"
echo ""
echo "💡 Tips:"
echo "  - If records are not pointing correctly, wait a few more minutes"
echo "  - DNS propagation can take up to 48 hours in some cases"
echo "  - You can check propagation status online at whatsmydns.net"