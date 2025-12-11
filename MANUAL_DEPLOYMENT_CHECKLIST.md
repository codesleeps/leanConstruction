# Manual Deployment Checklist

## Pre-Deployment Checklist

### System Requirements
- [ ] Ubuntu 20.04+ or compatible Linux distribution
- [ ] Root or sudo access
- [ ] At least 2GB RAM available
- [ ] At least 10GB disk space
- [ ] Internet connection for package downloads

### Required Packages
- [ ] Python 3.8+
- [ ] Node.js 16+ and npm
- [ ] Nginx web server
- [ ] PM2 process manager
- [ ] Git (for cloning if needed)

### DNS Preparation
- [ ] Domains registered and accessible
- [ ] VPS IP address noted
- [ ] DNS records prepared for update after deployment

---

## Step-by-Step Deployment

### Step 1: System Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx python3 python3-pip python3-venv nodejs npm pm2 curl wget git

# Verify installations
python3 --version
node --version
npm --version
nginx -v
pm2 --version
```

**Status**: [ ] Completed

### Step 2: Create Deployment Directory
```bash
# Create main deployment directory
sudo mkdir -p /var/www/lean-construction
sudo chown $USER:$USER /var/www/lean-construction
cd /var/www/lean-construction

# Create subdirectories
mkdir -p logs
```

**Status**: [ ] Completed

### Step 3: Deploy Backend Application
```bash
cd /var/www/lean-construction

# Extract backend files (if you have tar.gz file)
# tar -xzf lean-construction-backend.tar.gz

# OR clone from repository (if applicable)
# git clone <repository-url> .

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn[standard] gunicorn python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv

# If you have requirements.txt
# pip install -r requirements.txt
```

**Status**: [ ] Completed

### Step 4: Deploy Frontend Application
```bash
cd /var/www/lean-construction

# Extract frontend files (if you have separate frontend)
# mkdir -p frontend
# tar -xzf lean-construction-frontend.tar.gz -C frontend/

# OR if frontend is in same repository
cd frontend

# Install Node.js dependencies
npm install

# Create production environment file
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://yourdomain.com/api
REACT_APP_WS_URL=wss://yourdomain.com/ws
REACT_APP_ENVIRONMENT=production
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_key_here
EOF

# Build frontend for production
npm run build

# Verify build
ls -la build/
```

**Status**: [ ] Completed

### Step 5: Configure Nginx
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/lean-construction > /dev/null << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    root /var/www/lean-construction/frontend/build;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
sudo systemctl enable nginx
```

**Status**: [ ] Completed

### Step 6: Set Up PM2 Process Management
```bash
cd /var/www/lean-construction

# Create PM2 ecosystem configuration
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: 'uvicorn',
    args: 'app.main_lite:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/lean-construction',
    interpreter: 'none',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '2G',
    error_file: '/var/www/lean-construction/logs/pm2-error.log',
    out_file: '/var/www/lean-construction/logs/pm2-out.log',
    log_file: '/var/www/lean-construction/logs/pm2-combined.log',
    time: true
  }]
};
EOF

# Start application with PM2
source venv/bin/activate
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

**Status**: [ ] Completed

### Step 7: Configure Environment Variables
```bash
cd /var/www/lean-construction

# Create backend environment file
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=production
DEBUG=false
EOF

# Set proper permissions
chmod 600 .env
```

**Status**: [ ] Completed

### Step 8: Set Up SSL Certificates
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

**Status**: [ ] Completed

### Step 9: Configure Firewall
```bash
# Install and configure UFW
sudo apt install -y ufw

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (important!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**Status**: [ ] Completed

### Step 10: Set Up Monitoring
```bash
# Create monitoring script
sudo tee /usr/local/bin/app-monitor.sh > /dev/null << 'EOF'
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
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "Disk usage is ${DISK_USAGE}%, consider cleanup"
fi
EOF

# Make executable
sudo chmod +x /usr/local/bin/app-monitor.sh

# Add to crontab (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh >> /var/log/app-monitor.log 2>&1") | crontab -

# Create log file
sudo touch /var/log/app-monitor.log
sudo chmod 644 /var/log/app-monitor.log
```

**Status**: [ ] Completed

---

## Post-Deployment Verification

### Service Status Checks
```bash
# Check PM2 processes
pm2 status

# Check Nginx status
sudo systemctl status nginx

# Check if ports are listening
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# Test API health
curl http://localhost:8000/health

# Test frontend
curl http://localhost/

# Check application logs
pm2 logs lean-construction-api --lines 20
```

**API Health**: [ ] Working  
**Frontend**: [ ] Working  
**Nginx**: [ ] Running  
**PM2**: [ ] Running  

### DNS Configuration
```bash
# Update DNS records to point to your VPS IP
# yourdomain.com -> YOUR_VPS_IP
# www.yourdomain.com -> YOUR_VPS_IP

# Wait for DNS propagation (can take up to 48 hours)
# Test DNS resolution
nslookup yourdomain.com
dig yourdomain.com

# Test external access
curl -I http://yourdomain.com
curl -I https://yourdomain.com
```

**DNS Updated**: [ ] Yes  
**External Access**: [ ] Working  
**SSL Certificate**: [ ] Valid  

---

## Troubleshooting Checklist

### Common Issues and Solutions

#### Backend Not Starting
- [ ] Check Python environment: `source venv/bin/activate && python -c "import fastapi; print('OK')"`
- [ ] Check PM2 logs: `pm2 logs lean-construction-api`
- [ ] Verify port 8000 is not in use: `sudo netstat -tlnp | grep :8000`
- [ ] Check file permissions: `ls -la /var/www/lean-construction/`

#### Frontend Not Loading
- [ ] Verify build exists: `ls -la /var/www/lean-construction/frontend/build/`
- [ ] Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
- [ ] Test direct file access: `curl http://localhost/build/index.html`

#### Nginx Configuration Issues
- [ ] Test config syntax: `sudo nginx -t`
- [ ] Check Nginx status: `sudo systemctl status nginx`
- [ ] Reload configuration: `sudo systemctl reload nginx`

#### SSL Certificate Issues
- [ ] Verify domain DNS points to server: `nslookup yourdomain.com`
- [ ] Check Certbot logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`
- [ ] Test certificate: `openssl s_client -connect yourdomain.com:443 -servername yourdomain.com`

---

## Maintenance Commands

### Regular Maintenance
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python dependencies
source /var/www/lean-construction/venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Node.js dependencies
cd /var/www/lean-construction/frontend
npm update

# Clear PM2 logs
pm2 flush

# Restart services
pm2 restart all
sudo systemctl reload nginx

# Check disk usage
df -h
du -sh /var/www/lean-construction/

# Monitor system resources
top
free -h
```

### Backup Commands
```bash
# Create application backup
sudo tar -czf /backup/lean-construction-$(date +%Y%m%d).tar.gz /var/www/lean-construction/

# Backup Nginx configuration
sudo cp -r /etc/nginx /backup/nginx-config-$(date +%Y%m%d)/

# Backup PM2 ecosystem
cp /var/www/lean-construction/ecosystem.config.js /backup/
```

### Log Management
```bash
# View application logs
pm2 logs lean-construction-api

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u nginx -f
sudo journalctl -f

# Monitor log file sizes
sudo du -sh /var/log/nginx/
sudo du -sh /var/www/lean-construction/logs/
```

---

## Emergency Procedures

### Service Recovery
```bash
# Restart all services
pm2 restart all
sudo systemctl restart nginx

# Check if services are running
pm2 status
sudo systemctl status nginx

# If services won't start, check logs
pm2 logs lean-construction-api --lines 50
sudo journalctl -u nginx --lines 50
```

### Complete Recovery
```bash
# Stop all services
pm2 delete all
sudo systemctl stop nginx

# Restore from backup
sudo rm -rf /var/www/lean-construction
sudo mkdir -p /var/www/lean-construction
sudo tar -xzf /backup/lean-construction-LATEST.tar.gz -C /var/www/

# Restore permissions
sudo chown -R $USER:$USER /var/www/lean-construction
sudo chmod 755 /var/www/lean-construction

# Restart services
cd /var/www/lean-construction
source venv/bin/activate
pm2 start ecosystem.config.js
sudo systemctl start nginx
```

---

## Success Criteria

Deployment is successful when:
- [ ] Backend API responds to health checks
- [ ] Frontend loads without errors
- [ ] Nginx serves both applications correctly
- [ ] SSL certificates are installed and valid
- [ ] DNS records point to the correct IP
- [ ] All services are running and stable
- [ ] Monitoring and logging are working
- [ ] Firewall is configured properly
- [ ] Regular backups are in place

**Final Status**: [ ] Deployment Successful / [ ] Deployment Failed

---

**Deployment Completed**: ___________  
**Deployed By**: ___________  
**Server IP**: ___________  
**Domain**: ___________  
**Notes**: ___________