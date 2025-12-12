#!/bin/bash

# ============================================
# Production Deployment Orchestrator
# ============================================

set -e

echo "🚀 Lean Construction AI - Production Deployment Orchestrator"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_IP="srv1187860.hstgr.cloud"
DOMAIN_LEAN="constructionaipro.com"
DOMAIN_PIXEL="agentsflowai.cloud"
EMAIL="codesleep43@gmail.com"

# Function to print colored output
print_step() {
    echo -e "${BLUE}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if we're on the VPS
check_vps_environment() {
    print_step "Checking VPS environment..."
    
    if [[ $HOSTNAME == *"hstgr.cloud"* ]] || [[ $(hostname -I | grep -c "72.61.16.111") -gt 0 ]]; then
        print_success "Running on VPS environment"
        return 0
    else
        print_warning "Not running on VPS - some commands may not work"
        print_warning "This script should be run on: $VPS_IP"
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check for required commands
    for cmd in tar curl wget git nginx pm2 node npm python3 pip; do
        if ! command -v $cmd > /dev/null 2>&1; then
            missing_tools+=($cmd)
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install missing tools before continuing"
        exit 1
    fi
    
    print_success "All prerequisites available"
}

# Function to deploy backend
deploy_backend() {
    print_step "Phase 1: Deploying Backend"
    
    if [ -f "./fix-deployment-issues.sh" ]; then
        print_step "Running backend deployment fix..."
        chmod +x ./fix-deployment-issues.sh
        ./fix-deployment-issues.sh
        
        if [ $? -eq 0 ]; then
            print_success "Backend deployment completed"
            return 0
        else
            print_error "Backend deployment failed"
            return 1
        fi
    else
        print_error "Backend deployment script not found"
        return 1
    fi
}

# Function to deploy frontend
deploy_frontend() {
    print_step "Phase 2: Deploying Frontend"
    
    if [ -f "./deploy-frontend.sh" ]; then
        print_step "Running frontend deployment..."
        chmod +x ./deploy-frontend.sh
        ./deploy-frontend.sh
        
        if [ $? -eq 0 ]; then
            print_success "Frontend deployment completed"
            return 0
        else
            print_error "Frontend deployment failed"
            return 1
        fi
    else
        print_error "Frontend deployment script not found"
        return 1
    fi
}

# Function to configure nginx
configure_nginx() {
    print_step "Phase 3: Configuring Nginx"
    
    # Create nginx configuration
    sudo tee /etc/nginx/sites-available/lean-construction > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_LEAN www.$DOMAIN_LEAN;
    
    root /var/www/lean-construction/frontend/build;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location / {
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        print_success "Nginx configured successfully"
        return 0
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

# Function to setup SSL certificates
setup_ssl() {
    print_step "Phase 4: Setting up SSL Certificates"
    
    # Install certbot if not present
    if ! command -v certbot > /dev/null 2>&1; then
        print_step "Installing Certbot..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    # Setup SSL for both domains
    print_step "Setting up SSL for $DOMAIN_LEAN..."
    if sudo certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN --non-interactive --agree-tos --email $EMAIL; then
        print_success "SSL certificate installed for $DOMAIN_LEAN"
    else
        print_error "SSL certificate installation failed for $DOMAIN_LEAN"
        return 1
    fi
    
    print_step "Setting up SSL for $DOMAIN_PIXEL..."
    if sudo certbot --nginx -d $DOMAIN_PIXEL -d www.$DOMAIN_PIXEL --non-interactive --agree-tos --email $EMAIL; then
        print_success "SSL certificate installed for $DOMAIN_PIXEL"
    else
        print_warning "SSL certificate installation failed for $DOMAIN_PIXEL (continuing...)"
    fi
    
    # Test auto-renewal
    sudo certbot renew --dry-run > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "SSL auto-renewal configured"
    else
        print_warning "SSL auto-renewal test failed"
    fi
    
    return 0
}

# Function to configure monitoring
setup_monitoring() {
    print_step "Phase 5: Setting up Monitoring"
    
    # Create monitoring script
    sudo tee /usr/local/bin/app-monitor.sh > /dev/null <<'EOF'
#!/bin/bash

# Check if PM2 processes are running
if ! pm2 list | grep -q "online"; then
    echo "PM2 processes not running, restarting..."
    pm2 restart all
fi

# Check Nginx
if ! systemctl is-active --quiet nginx; then
    echo "Nginx not running, restarting..."
    sudo systemctl restart nginx
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "Disk usage is ${DISK_USAGE}%, consider cleanup"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "Memory usage is ${MEM_USAGE}%, check processes"
fi
EOF

    sudo chmod +x /usr/local/bin/app-monitor.sh
    
    # Add monitoring to cron
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh >> /var/log/app-monitor.log 2>&1") | crontab -
    
    print_success "Monitoring configured"
}

# Function to run final tests
run_tests() {
    print_step "Phase 6: Running Final Tests"
    
    # Test backend API
    print_step "Testing backend API..."
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend API responding"
    else
        print_error "Backend API not responding"
        return 1
    fi
    
    # Test frontend
    print_step "Testing frontend..."
    if curl -s http://localhost/ > /dev/null; then
        print_success "Frontend accessible"
    else
        print_error "Frontend not accessible"
        return 1
    fi
    
    # Test SSL (if domains are configured)
    print_step "Testing SSL certificates..."
    if command -v openssl > /dev/null 2>&1; then
        if echo | openssl s_client -servername $DOMAIN_LEAN -connect $DOMAIN_LEAN:443 > /dev/null 2>&1; then
            print_success "SSL certificate valid for $DOMAIN_LEAN"
        else
            print_warning "SSL certificate test failed for $DOMAIN_LEAN (may need DNS configuration)"
        fi
    fi
    
    print_success "All tests completed"
}

# Function to show final status
show_final_status() {
    echo ""
    echo "🎉 PRODUCTION DEPLOYMENT COMPLETED!"
    echo "=================================="
    echo ""
    echo "📊 Deployment Summary:"
    echo "✅ Backend API: Running on port 8000"
    echo "✅ Frontend: Built and served by Nginx"
    echo "✅ Nginx: Configured and running"
    echo "✅ SSL: Certificates installed"
    echo "✅ Monitoring: Automated health checks active"
    echo ""
    echo "🌐 Access Points:"
    echo "• Backend API: https://$DOMAIN_LEAN/api/"
    echo "• API Docs: https://$DOMAIN_LEAN/docs"
    echo "• Frontend: https://$DOMAIN_LEAN"
    echo "• Health Check: https://$DOMAIN_LEAN/api/health"
    echo ""
    echo "📋 Management Commands:"
    echo "• Check status: ./check-deployment-status.sh"
    echo "• View logs: pm2 logs"
    echo "• Restart services: pm2 restart all"
    echo "• Monitor: /usr/local/bin/app-monitor.sh"
    echo ""
    echo "⚠️  Next Steps Required:"
    echo "1. Update DNS records to point to: $VPS_IP"
    echo "   - $DOMAIN_LEAN → $VPS_IP"
    echo "   - $DOMAIN_PIXEL → $VPS_IP"
    echo "2. Wait for DNS propagation (up to 48 hours)"
    echo "3. Verify SSL certificates are working"
    echo "4. Configure production environment variables"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "• Check logs: pm2 logs lean-construction-api"
    echo "• Check status: sudo systemctl status nginx"
    echo "• Test connectivity: curl -I https://$DOMAIN_LEAN"
    echo ""
}

# Main deployment flow
main() {
    echo "Starting production deployment process..."
    echo ""
    
    # Check environment
    check_vps_environment || {
        echo ""
        print_error "This script must be run on the VPS ($VPS_IP)"
        echo "Please SSH into the VPS and run this script there."
        exit 1
    }
    
    # Check prerequisites
    check_prerequisites
    
    # Execute deployment phases
    deploy_backend || exit 1
    deploy_frontend || exit 1
    configure_nginx || exit 1
    setup_ssl || exit 1
    setup_monitoring
    run_tests || exit 1
    
    # Show final status
    show_final_status
}

# Run main function
main "$@"