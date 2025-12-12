#!/bin/bash

# ============================================
# SSL Certificate Installation Script
# ============================================

echo "🔒 Installing SSL Certificates with Let's Encrypt"
echo "=============================================="

# Define domains
DOMAIN_LEAN="constructionaipro.com"
DOMAIN_PIXEL="agentsflowai.cloud"

echo "🔧 Installing Certbot and Nginx plugin..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo "📧 Setting up SSL certificates for $DOMAIN_LEAN..."
sudo certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN --non-interactive --agree-tos --email admin@$DOMAIN_LEAN

echo "📧 Setting up SSL certificates for $DOMAIN_PIXEL..."
sudo certbot --nginx -d $DOMAIN_PIXEL -d www.$DOMAIN_PIXEL --non-interactive --agree-tos --email admin@$DOMAIN_PIXEL

echo "🔄 Testing certificate renewal process..."
sudo certbot renew --dry-run

echo ""
echo "✅ SSL Certificate Installation Complete!"
echo "====================================="
echo "🌐 Your sites are now secured with HTTPS:"
echo "   https://$DOMAIN_LEAN"
echo "   https://www.$DOMAIN_LEAN"
echo "   https://$DOMAIN_PIXEL"
echo "   https://www.$DOMAIN_PIXEL"
echo ""
echo "📅 Certificates will automatically renew before expiration"
echo "📋 To manually check certificates: sudo certbot certificates"
echo "🔄 To manually renew certificates: sudo certbot renew"