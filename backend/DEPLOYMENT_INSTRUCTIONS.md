# Lean Construction AI - Backend Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the Lean Construction AI backend to the VPS server at `srv1187860.hstgr.cloud` (72.61.16.111).

## Prerequisites

- SSH access to VPS: `ssh root@srv1187860.hstgr.cloud` or `ssh root@72.61.16.111`
- SSH public key available in `SSH_PUBLIC_KEY.txt`
- Nginx installed and running on port 80
- PM2 installed on VPS
- Python 3.8+ installed on VPS

## Deployment Steps

### 1. Establish SSH Access

```bash
ssh root@srv1187860.hstgr.cloud
# or
ssh root@72.61.16.111
```

If password authentication fails, use the SSH key from `SSH_PUBLIC_KEY.txt`:

```bash
ssh -i ~/.ssh/id_rsa root@srv1187860.hstgr.cloud
```

### 2. Upload Deployment Files

From your local machine, upload the necessary files to the VPS:

```bash
# Upload backend package
scp /tmp/lean-construction-backend.tar.gz root@srv1187860.hstgr.cloud:/tmp/

# Upload deployment scripts
scp legacy_scripts/production-deployment-orchestrator.sh root@srv1187860.hstgr.cloud:/root/deployment-scripts/
scp legacy_scripts/fix-deployment-issues.sh root@srv1187860.hstgr.cloud:/root/deployment-scripts/
scp legacy_scripts/fix-backend-deployment.sh root@srv1187860.hstgr.cloud:/root/deployment-scripts/
scp legacy_scripts/check-deployment-status.sh root@srv1187860.hstgr.cloud:/root/deployment-scripts/
```

### 3. Deploy Backend

On the VPS, run the deployment script:

```bash
cd /root/deployment-scripts
chmod +x *.sh
./fix-deployment-issues.sh
```

This script will:
- Clean existing deployment
- Create directory structure at `/var/www/lean-construction`
- Extract backend package
- Create Python virtual environment
- Install dependencies
- Configure PM2
- Start backend service

### 4. Verify Backend

Check that the backend is running:

```bash
# Check PM2 status
pm2 status

# Test health endpoint
curl -v http://localhost:8000/health

# Test API docs
curl http://localhost:8000/docs

# Check logs
pm2 logs lean-construction-api --lines 50
```

### 5. Configure Nginx

Create or update Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/lean-construction
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name constructionaipro.com www.constructionaipro.com;

    root /var/www/lean-construction/frontend/build;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    # Static files
    location / {
        try_files $uri $uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

Enable the site and reload Nginx:

```bash
sudo ln -sf /etc/nginx/sites-available/lean-construction /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cd /var/www/lean-construction
nano .env
```

Add the following content:

```env
DATABASE_URL=sqlite:///./lean_construction.db
SECRET_KEY=<generate-random-64-char-string>
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://constructionaipro.com","https://www.constructionaipro.com"]
```

Generate a secure SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Set proper permissions:

```bash
chmod 600 .env
```

### 7. Configure Monitoring

The deployment script automatically configures health monitoring. To verify:

```bash
# Check cron jobs
crontab -l

# Test health check manually
/usr/local/bin/lean-construction-healthcheck.sh
```

### 8. Test External Access

From your local machine, test the backend:

```bash
curl -v http://72.61.16.111/health
curl -v http://72.61.16.111/api/health
```

## Troubleshooting

### Backend Not Responding

```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs lean-construction-api --lines 100

# Check if port is open
netstat -tlnp | grep 8000

# Test import manually
cd /var/www/lean-construction
source venv/bin/activate
python -c "from app.main_lite import app; print('Import successful')"
```

### ModuleNotFoundError

Ensure PYTHONPATH is set correctly in PM2 configuration:

```bash
# Check ecosystem.config.js
nano /var/www/lean-construction/ecosystem.config.js

# Ensure PYTHONPATH includes /var/www/lean-construction
```

### Nginx Proxy Issues

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify proxy configuration
sudo cat /etc/nginx/sites-enabled/default | grep proxy_pass
```

## Success Criteria

- ✅ SSH access established to VPS
- ✅ Backend package extracted to `/var/www/lean-construction`
- ✅ Python virtual environment created and activated
- ✅ All dependencies installed successfully
- ✅ PM2 configured with correct PYTHONPATH
- ✅ Backend service running under PM2 management
- ✅ Health endpoint returns HTTP 200: `http://localhost:8000/health`
- ✅ API documentation accessible: `http://localhost:8000/docs`
- ✅ External access works: `http://72.61.16.111/health`
- ✅ PM2 status shows "online" with stable uptime
- ✅ No errors in PM2 logs
- ✅ Health check monitoring configured and running

## Next Steps

1. **Phase 2**: SSL certificate installation
2. **Phase 3**: Database initialization and migrations
3. **Phase 4**: Frontend deployment

## File Structure

```
/var/www/lean-construction/
├── venv/                          # Python virtual environment
│   ├── bin/
│   │   ├── python
│   │   ├── pip
│   │   └── uvicorn
│   └── lib/python3.11/site-packages/
├── app/                           # Backend application
│   ├── __init__.py
│   ├── main.py                    # Full-featured entry point
│   ├── main_lite.py              # Lightweight entry point (USED)
│   ├── main_production.py        # Production entry point
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── payments.py
│   │   ├── ml_routes.py
│   │   └── onboarding.py
│   ├── ml/
│   ├── integrations/
│   └── middleware/
├── alembic/                       # Database migrations
├── logs/                          # Application logs
│   ├── pm2-error.log
│   ├── pm2-out.log
│   └── backend.log
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── ecosystem.config.js            # PM2 configuration
└── database.py                    # Database setup
```

## Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `ecosystem.config.js` | PM2 process config | Entry point: `app.main_lite:app`, PYTHONPATH, port 8000 |
| `.env` | Environment variables | DATABASE_URL, SECRET_KEY, ENVIRONMENT=production |
| `/etc/nginx/sites-enabled/default` | Nginx reverse proxy | Proxy `/api/*` to `localhost:8000` |
| `/etc/systemd/system/lean-construction-backend.service` | Systemd service | Backup process manager |
| `/usr/local/bin/lean-construction-healthcheck.sh` | Health monitoring | Auto-restart on failure |

## Management Commands

```bash
# PM2 Commands
pm2 status                    # Check service status
pm2 logs lean-construction-api  # View logs
pm2 restart lean-construction-api  # Restart service
pm2 stop lean-construction-api     # Stop service
pm2 start lean-construction-api    # Start service
pm2 save                       # Save process list
pm2 monit                      # Monitor resources

# Systemd Commands
sudo systemctl status lean-construction-backend  # Check status
sudo systemctl restart lean-construction-backend   # Restart
sudo systemctl enable lean-construction-backend    # Enable on boot

# Health Check
/usr/local/bin/lean-construction-healthcheck.sh  # Manual check
```

## Support

For issues or questions, refer to the main deployment documentation or contact the development team.
