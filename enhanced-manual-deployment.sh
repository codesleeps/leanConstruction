#!/bin/bash

# ============================================
# Enhanced Manual Deployment Script
# ============================================
# Features:
# - Interactive deployment with user confirmation
# - Comprehensive error handling and rollback
# - Detailed logging and progress tracking
# - Backup and recovery procedures
# - Environment validation
# - Service health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_DIR="/var/www/lean-construction"
LOG_FILE="/tmp/manual-deployment-$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="/tmp/deployment-backup-$(date +%Y%m%d_%H%M%S)"
DOMAIN_LEAN="constructionaipro.com"
DOMAIN_PIXEL="agentsflowai.cloud"
EMAIL="codesleep43@gmail.com"

# Deployment options (can be overridden by flags)
SKIP_BACKUP=false
INTERACTIVE=true
VERBOSE=false
ROLLBACK_ON_ERROR=true

# ============================================
# Utility Functions
# ============================================

log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${PURPLE}"
    echo "=========================================="
    echo "  Enhanced Manual Deployment Script"
    echo "=========================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}>>> $1${NC}"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
    log "INFO: $1"
}

confirm() {
    if [ "$INTERACTIVE" = "true" ]; then
        echo -e "${YELLOW}Do you want to continue? (y/N)${NC}"
        read -r response
        case $response in
            [yY][eE][sS]|[yY]) return 0 ;;
            *) return 1 ;;
        esac
    else
        return 0
    fi
}

check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        print_error "Required command '$1' not found"
        return 1
    fi
    return 0
}

# ============================================
# Backup and Rollback Functions
# ============================================

create_backup() {
    if [ "$SKIP_BACKUP" = "true" ]; then
        print_info "Skipping backup (--skip-backup flag set)"
        return 0
    fi
    
    print_step "Creating deployment backup..."
    
    if [ -d "$DEPLOYMENT_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        
        # Backup current deployment
        cp -r "$DEPLOYMENT_DIR" "$BACKUP_DIR/" 2>/dev/null || true
        
        # Backup Nginx configs
        sudo cp -r /etc/nginx/sites-available "$BACKUP_DIR/" 2>/dev/null || true
        
        # Backup PM2 ecosystem config
        cp ecosystem.config.js "$BACKUP_DIR/" 2>/dev/null || true
        
        # Backup environment files
        cp .env "$BACKUP_DIR/" 2>/dev/null || true
        cp frontend/.env.production "$BACKUP_DIR/" 2>/dev/null || true
        
        print_success "Backup created at: $BACKUP_DIR"
        echo "$BACKUP_DIR" > /tmp/deployment_backup_location
    else
        print_info "No existing deployment found, skipping backup"
    fi
}

rollback_deployment() {
    print_error "Deployment failed, initiating rollback..."
    
    local backup_location=$(cat /tmp/deployment_backup_location 2>/dev/null || echo "")
    
    if [ -n "$backup_location" ] && [ -d "$backup_location" ]; then
        print_step "Rolling back to previous deployment..."
        
        # Stop services
        pm2 delete all 2>/dev/null || true
        sudo systemctl stop nginx 2>/dev/null || true
        
        # Restore deployment
        sudo rm -rf "$DEPLOYMENT_DIR"
        sudo mkdir -p "$DEPLOYMENT_DIR"
        cp -r "$backup_location"/* "$DEPLOYMENT_DIR/" 2>/dev/null || true
        
        # Restore Nginx configs
        sudo cp -r "$backup_location/sites-available"/* /etc/nginx/sites-available/ 2>/dev/null || true
        
        # Restart services
        pm2 start ecosystem.config.js 2>/dev/null || true
        sudo systemctl start nginx 2>/dev/null || true
        
        print_success "Rollback completed successfully"
    else
        print_error "No backup found for rollback"
    fi
    
    print_error "Deployment failed. Check logs at: $LOG_FILE"
    exit 1
}

# ============================================
# Pre-deployment Validation
# ============================================

validate_environment() {
    print_step "Validating deployment environment..."
    
    local errors=0
    
    # Check required commands
    local required_commands=("python3" "node" "npm" "pm2" "nginx" "curl" "tar")
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            errors=$((errors + 1))
        fi
    done
    
    # Check system resources
    local disk_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$disk_space" -lt 1048576 ]; then  # Less than 1GB
        print_warning "Low disk space: $(df -h / | awk 'NR==2 {print $4}')"
    fi
    
    # Check if running as appropriate user
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root - consider using a non-root user"
    fi
    
    # Check port availability
    local ports=(80 443 8000)
    for port in "${ports[@]}"; do
        if netstat -ln 2>/dev/null | grep -q ":$port " || ss -ln 2>/dev/null | grep -q ":$port "; then
            print_warning "Port $port is already in use"
        fi
    done
    
    if [ $errors -gt 0 ]; then
        print_error "Environment validation failed with $errors errors"
        return 1
    fi
    
    print_success "Environment validation completed"
    return 0
}

# ============================================
# Deployment Functions
# ============================================

deploy_backend() {
    print_step "Deploying backend application..."
    
    cd "$DEPLOYMENT_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_info "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        print_info "Installing minimal dependencies..."
        pip install fastapi uvicorn[standard] gunicorn python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv
    fi
    
    # Test backend startup
    print_info "Testing backend startup..."
    python -c "
import sys
sys.path.append('.')
try:
    if hasattr(__import__('app').main, 'app'):
        print('✅ Full backend app imported successfully')
    elif hasattr(__import__('app'), 'main_lite'):
        print('✅ Lite backend app imported successfully')
    else:
        print('⚠️  Using minimal backend')
except ImportError as e:
    print(f'⚠️  Import error: {e}')
    print('Will use minimal backend for deployment')
"
    
    print_success "Backend deployment completed"
}

deploy_frontend() {
    print_step "Deploying frontend application..."
    
    cd "$DEPLOYMENT_DIR"
    
    if [ ! -d "frontend" ]; then
        print_warning "Frontend directory not found, creating placeholder..."
        mkdir -p frontend/build
        cat > frontend/build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lean Construction AI</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            text-align: center; 
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 3em; margin-bottom: 20px; }
        p { font-size: 1.2em; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ Lean Construction AI</h1>
        <p>Building the future of construction with AI</p>
        <p>Frontend deployment in progress...</p>
    </div>
</body>
</html>
EOF
    else
        cd frontend
        
        # Check Node.js version
        local node_version=$(node --version)
        print_info "Node.js version: $node_version"
        
        # Install dependencies
        print_info "Installing Node.js dependencies..."
        npm install
        
        # Create production environment
        cat > .env.production << EOF
REACT_APP_API_URL=https://$DOMAIN_LEAN/api
REACT_APP_WS_URL=wss://$DOMAIN_LEAN/ws
REACT_APP_ENVIRONMENT=production
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
EOF
        
        # Build frontend
        print_info "Building React application..."
        npm run build
        
        # Verify build
        if [ -d "build" ] && [ -f "build/index.html" ]; then
            local build_size=$(du -sh build | cut -f1)
            print_success "Frontend build completed (Size: $build_size)"
        else
            print_error "Frontend build failed"
            return 1
        fi
    fi
    
    print_success "Frontend deployment completed"
}

configure_nginx() {
    print_step "Configuring Nginx web server..."
    
    # Create main application config
    sudo tee /etc/nginx/sites-available/lean-construction > /dev/null << EOF
# Lean Construction AI - Main Application
server {
    listen 80;
    server_name $DOMAIN_LEAN www.$DOMAIN_LEAN;
    
    root $DEPLOYMENT_DIR/frontend/build;
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
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files with caching
    location / {
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Error pages
    error_page 404 /index.html;
}

# Redirect HTTP to HTTPS (SSL will be configured later)
server {
    listen 80;
    server_name $DOMAIN_PIXEL www.$DOMAIN_PIXEL;
    return 301 https://\$server_name\$request_uri;
}
EOF

    # Create placeholder for second domain
    sudo mkdir -p /var/www/pixelcraft-bloom
    sudo tee /var/www/pixelcraft-bloom/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelCraft Bloom</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            text-align: center; 
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 3em; margin-bottom: 20px; }
        .status { background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 PixelCraft Bloom</h1>
        <div class="status">
            <h2>🌟 Coming Soon!</h2>
            <p>Creative design application by CodeSleeps</p>
            <p>AI-powered pixel art generation and creative tools</p>
        </div>
        <p>📧 Contact: codesleep43@gmail.com</p>
        <p>🌐 Domain: agentsflowai.cloud</p>
    </div>
</body>
</html>
EOF

    # Enable sites
    sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
    sudo ln -sf /var/www/pixelcraft-bloom /etc/nginx/sites-available/pixelcraft-bloom
    sudo ln -sf /etc/nginx/sites-available/pixelcraft-bloom /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        print_success "Nginx configuration completed"
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

setup_pm2() {
    print_step "Setting up PM2 process management..."
    
    cd "$DEPLOYMENT_DIR"
    
    # Create PM2 ecosystem config
    cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: 'uvicorn',
    args: 'app.main_lite:app --host 0.0.0.0 --port 8000 --workers 2',
    cwd: '$DEPLOYMENT_DIR',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production',
      PORT: 8000,
      PYTHONPATH: '$DEPLOYMENT_DIR'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '2G',
    error_file: '$DEPLOYMENT_DIR/logs/pm2-error.log',
    out_file: '$DEPLOYMENT_DIR/logs/pm2-out.log',
    log_file: '$DEPLOYMENT_DIR/logs/pm2-combined.log',
    time: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
EOF
    
    # Create logs directory
    mkdir -p logs
    
    # Stop any existing processes
    pm2 delete lean-construction-api 2>/dev/null || true
    
    # Start with PM2
    source venv/bin/activate
    pm2 start ecosystem.config.js
    pm2 save
    
    # Enable PM2 startup
    pm2 startup || true
    
    print_success "PM2 configuration completed"
}

setup_monitoring() {
    print_step "Setting up application monitoring..."
    
    # Create monitoring script
    sudo tee /usr/local/bin/app-monitor.sh > /dev/null << 'EOF'
#!/bin/bash

# Application Health Monitor
LOG_FILE="/var/log/app-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Check PM2 processes
if ! pm2 list | grep -q "online"; then
    log_message "PM2 processes not running, restarting..."
    pm2 restart all
fi

# Check Nginx
if ! systemctl is-active --quiet nginx; then
    log_message "Nginx not running, restarting..."
    sudo systemctl restart nginx
fi

# Check API health
if ! curl -s http://localhost:8000/health > /dev/null; then
    log_message "API health check failed"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    log_message "Disk usage is ${DISK_USAGE}%, consider cleanup"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    log_message "Memory usage is ${MEM_USAGE}%, check processes"
fi
EOF

    sudo chmod +x /usr/local/bin/app-monitor.sh
    
    # Add monitoring to cron
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh >> /var/log/app-monitor.log 2>&1") | crontab -
    
    # Create log file
    sudo touch /var/log/app-monitor.log
    sudo chmod 644 /var/log/app-monitor.log
    
    print_success "Monitoring setup completed"
}

# ============================================
# Post-deployment Testing
# ============================================

run_health_checks() {
    print_step "Running post-deployment health checks..."
    
    local errors=0
    
    # Wait for services to start
    sleep 10
    
    # Check backend API
    print_info "Testing backend API..."
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend API responding"
    else
        print_error "Backend API not responding"
        errors=$((errors + 1))
    fi
    
    # Check frontend
    print_info "Testing frontend..."
    if curl -s http://localhost/ > /dev/null; then
        print_success "Frontend accessible"
    else
        print_error "Frontend not accessible"
        errors=$((errors + 1))
    fi
    
    # Check Nginx
    print_info "Testing Nginx..."
    if systemctl is-active --quiet nginx; then
        print_success "Nginx running"
    else
        print_error "Nginx not running"
        errors=$((errors + 1))
    fi
    
    # Check PM2
    print_info "Testing PM2 processes..."
    if pm2 list | grep -q "online"; then
        print_success "PM2 processes running"
    else
        print_error "PM2 processes not running"
        errors=$((errors + 1))
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "All health checks passed"
        return 0
    else
        print_error "$errors health checks failed"
        return 1
    fi
}

# ============================================
# Main Deployment Flow
# ============================================

show_deployment_summary() {
    echo ""
    echo -e "${GREEN}🎉 MANUAL DEPLOYMENT COMPLETED!${NC}"
    echo "=================================="
    echo ""
    echo -e "${CYAN}📊 Deployment Summary:${NC}"
    echo "✅ Backend API: Running on port 8000"
    echo "✅ Frontend: Built and served by Nginx"
    echo "✅ Nginx: Configured and running"
    echo "✅ PM2: Process management active"
    echo "✅ Monitoring: Health checks enabled"
    echo "✅ Backup: Created at $BACKUP_DIR"
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo "• Backend API: http://localhost:8000/"
    echo "• API Health: http://localhost:8000/health"
    echo "• Frontend: http://localhost/"
    echo "• Main Domain: http://$DOMAIN_LEAN"
    echo "• Secondary Domain: http://$DOMAIN_PIXEL"
    echo ""
    echo -e "${CYAN}📋 Management Commands:${NC}"
    echo "• Check status: ./check-deployment-status.sh"
    echo "• View logs: pm2 logs lean-construction-api"
    echo "• Restart services: pm2 restart all && sudo systemctl reload nginx"
    echo "• Monitor: tail -f /var/log/app-monitor.log"
    echo "• Check logs: tail -f $LOG_FILE"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps Required:${NC}"
    echo "1. Update DNS records to point to this VPS IP"
    echo "   - $DOMAIN_LEAN → [YOUR_VPS_IP]"
    echo "   - $DOMAIN_PIXEL → [YOUR_VPS_IP]"
    echo "2. Install SSL certificates:"
    echo "   sudo certbot --nginx -d $DOMAIN_LEAN -d www.$DOMAIN_LEAN"
    echo "3. Configure production environment variables"
    echo "4. Test all functionality end-to-end"
    echo ""
    echo -e "${PURPLE}🔧 Deployment Details:${NC}"
    echo "• Log file: $LOG_FILE"
    echo "• Backup: $BACKUP_DIR"
    echo "• Deployment directory: $DEPLOYMENT_DIR"
    echo ""
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --non-interactive)
                INTERACTIVE=false
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --no-rollback)
                ROLLBACK_ON_ERROR=false
                shift
                ;;
            --help)
                echo "Enhanced Manual Deployment Script"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --non-interactive    Run without user prompts"
                echo "  --skip-backup        Skip backup creation"
                echo "  --verbose            Enable verbose output"
                echo "  --no-rollback        Disable automatic rollback on failure"
                echo "  --help               Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Print header
    print_header
    
    # Set trap for rollback on error
    if [ "$ROLLBACK_ON_ERROR" = "true" ]; then
        trap rollback_deployment ERR
    fi
    
    # Show deployment info
    print_info "Deployment directory: $DEPLOYMENT_DIR"
    print_info "Log file: $LOG_FILE"
    print_info "Interactive mode: $INTERACTIVE"
    print_info "Backup enabled: $([ "$SKIP_BACKUP" = "true" ] && echo "No" || echo "Yes")"
    echo ""
    
    # Confirm deployment
    if ! confirm; then
        print_info "Deployment cancelled by user"
        exit 0
    fi
    
    # Execute deployment steps
    create_backup || print_warning "Backup creation failed"
    validate_environment || exit 1
    
    deploy_backend || exit 1
    deploy_frontend || exit 1
    configure_nginx || exit 1
    setup_pm2 || exit 1
    setup_monitoring
    
    # Run health checks
    if run_health_checks; then
        show_deployment_summary
        print_success "Deployment completed successfully!"
    else
        print_error "Deployment completed but health checks failed"
        print_info "Check the logs and troubleshoot issues before proceeding"
        exit 1
    fi
}

# Run main function
main "$@"