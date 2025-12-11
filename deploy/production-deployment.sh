#!/bin/bash

# Production Deployment Script for Lean AI Construction Customer Onboarding System
# This script automates the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="lean-construction-onboarding"
BACKEND_DIR="../backend"
FRONTEND_DIR="../website"
ENV_FILE=".env.production"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("python3" "pip" "node" "npm" "git" "docker" "docker-compose")
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "$tool is not installed. Please install it first."
            exit 1
        fi
    done
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        warning "Environment file $ENV_FILE not found. Creating from template..."
        cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
        warning "Please edit $ENV_FILE with your production configuration before continuing."
        read -p "Press enter when you have configured the environment file..."
    fi
    
    log "Prerequisites check completed."
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if using PostgreSQL
    if grep -q "postgresql" "$ENV_FILE" 2>/dev/null; then
        local db_url=$(grep "DATABASE_URL" "$ENV_FILE" | cut -d'=' -f2)
        if [[ -n "$db_url" ]]; then
            info "Backing up PostgreSQL database..."
            pg_dump "$db_url" > "$BACKUP_DIR/database_backup.sql"
        fi
    fi
    
    # Backup existing application files
    if [[ -d "$BACKEND_DIR" ]]; then
        cp -r "$BACKEND_DIR" "$BACKUP_DIR/backend_backup"
    fi
    
    if [[ -d "$FRONTEND_DIR" ]]; then
        cp -r "$FRONTEND_DIR" "$BACKUP_DIR/frontend_backup"
    fi
    
    log "Backup created at: $BACKUP_DIR"
}

# Setup backend
setup_backend() {
    log "Setting up backend..."
    
    cd "$BACKEND_DIR"
    
    # Install Python dependencies
    info "Installing Python dependencies..."
    pip install -r requirements-production.txt
    
    # Run database migrations
    info "Running database migrations..."
    if command -v alembic &> /dev/null; then
        alembic upgrade head
    else
        warning "Alembic not found. Running direct database creation..."
        python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
    fi
    
    # Create necessary directories
    mkdir -p logs uploads
    
    cd - > /dev/null
    
    log "Backend setup completed."
}

# Setup frontend
setup_frontend() {
    log "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install Node.js dependencies
    info "Installing Node.js dependencies..."
    npm ci --production
    
    # Build the application
    info "Building frontend application..."
    npm run build
    
    cd - > /dev/null
    
    log "Frontend setup completed."
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start backend service
    info "Starting backend service..."
    cd "$BACKEND_DIR"
    
    # Create systemd service file
    sudo tee /etc/systemd/system/lean-construction-backend.service > /dev/null << EOF
[Unit]
Description=Lean Construction Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable lean-construction-backend
    sudo systemctl start lean-construction-backend
    
    cd - > /dev/null
    
    # Start frontend with nginx
    info "Configuring nginx..."
    sudo tee /etc/nginx/sites-available/lean-construction > /dev/null << EOF
server {
    listen 80;
    server_name leanaiconstruction.com www.leanaiconstruction.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name leanaiconstruction.com www.leanaiconstruction.com;
    
    ssl_certificate /etc/letsencrypt/live/leanaiconstruction.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/leanaiconstruction.com/privkey.pem;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \$host;
    }
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    sudo nginx -t
    
    # Restart nginx
    sudo systemctl restart nginx
    
    log "Services started successfully."
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create health check script
    sudo tee /usr/local/bin/lean-construction-healthcheck.sh > /dev/null << 'EOF'
#!/bin/bash

# Health check script for Lean Construction services

API_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Check backend
if curl -f -s "$API_URL" > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    systemctl restart lean-construction-backend
fi

# Check frontend
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
    systemctl restart nginx
fi
EOF
    
    sudo chmod +x /usr/local/bin/lean-construction-healthcheck.sh
    
    # Add to crontab for regular health checks
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/lean-construction-healthcheck.sh >> /var/log/lean-construction-health.log 2>&1") | crontab -
    
    log "Monitoring setup completed."
}

# Run tests
run_tests() {
    log "Running tests..."
    
    # Backend tests
    cd "$BACKEND_DIR"
    if [[ -f "pytest.ini" ]]; then
        python -m pytest tests/ -v
    fi
    
    # Frontend tests
    cd "$FRONTEND_DIR"
    if [[ -f "package.json" ]] && npm run test --if-present > /dev/null 2>&1; then
        npm run test
    fi
    
    cd - > /dev/null
    
    log "Tests completed."
}

# SSL certificate setup
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        info "Installing certbot..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    # Get SSL certificate
    info "Obtaining SSL certificate..."
    sudo certbot --nginx -d leanaiconstruction.com -d www.leanaiconstruction.com --non-interactive --agree-tos --email admin@leanaiconstruction.com
    
    # Setup auto-renewal
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer
    
    log "SSL setup completed."
}

# Main deployment function
main() {
    log "Starting production deployment for $PROJECT_NAME"
    
    # Confirmation
    read -p "This will deploy the customer onboarding system to production. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Deployment cancelled."
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    create_backup
    setup_backend
    setup_frontend
    run_tests
    start_services
    setup_monitoring
    setup_ssl
    
    log "Deployment completed successfully!"
    log "Your application is now live at:"
    log "  - Website: https://leanaiconstruction.com"
    log "  - API: https://api.leanaiconstruction.com"
    log "  - Dashboard: https://app.leanaiconstruction.com"
    log ""
    log "Next steps:"
    log "1. Configure DNS records to point to your server"
    log "2. Set up monitoring and alerting"
    log "3. Configure backup schedules"
    log "4. Test the onboarding flow end-to-end"
    
    info "Check logs with: sudo journalctl -u lean-construction-backend -f"
    info "Monitor health with: /usr/local/bin/lean-construction-healthcheck.sh"
}

# Handle script arguments
case "${1:-}" in
    --check-prerequisites)
        check_prerequisites
        ;;
    --backup)
        create_backup
        ;;
    --setup-backend)
        setup_backend
        ;;
    --setup-frontend)
        setup_frontend
        ;;
    --start-services)
        start_services
        ;;
    --setup-monitoring)
        setup_monitoring
        ;;
    --setup-ssl)
        setup_ssl
        ;;
    --run-tests)
        run_tests
        ;;
    --help|-h)
        echo "Production Deployment Script for Lean AI Construction"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  --check-prerequisites    Check if all required tools are installed"
        echo "  --backup                Create backup of existing installation"
        echo "  --setup-backend         Setup and configure backend services"
        echo "  --setup-frontend        Setup and build frontend application"
        echo "  --start-services        Start all services (backend, nginx, etc.)"
        echo "  --setup-monitoring      Configure health checks and monitoring"
        echo "  --setup-ssl            Setup SSL certificates with Let's Encrypt"
        echo "  --run-tests            Run application tests"
        echo "  --help, -h             Show this help message"
        echo ""
        echo "Run without arguments to start full deployment process."
        ;;
    *)
        main
        ;;
esac