# VPS Deployment Checklist

## VPS Specifications Confirmed
- ✅ **Hostname**: srv1187860.hstgr.cloud
- ✅ **CPU**: 4 vCPU cores
- ✅ **RAM**: 16 GB
- ✅ **Storage**: 200 GB NVMe disk
- ✅ **Bandwidth**: 16 TB
- ✅ **OS**: Ubuntu 24.04 LTS

## Pre-deployment Preparation
- ✅ Verify tar.gz files contain application code
- ✅ Create modified deployment script for local files
- ✅ Test deployment script in simulation environment
- ✅ Prepare DNS configuration details

## Deployment Steps

### 1. Connect to VPS
```bash
ssh root@srv1187860.hstgr.cloud
```

### 2. Transfer Files to VPS
- Transfer lean-construction-backend.tar.gz
- Transfer lean-construction-frontend.tar.gz
- Transfer modified-vps-deployment.sh

### 3. Run Deployment Script
```bash
chmod +x modified-vps-deployment.sh
./modified-vps-deployment.sh
```

### 4. DNS Configuration
Update DNS A records to point:
- leanaiconstruction.com → 72.61.16.111
- www.leanaiconstruction.com → 72.61.16.111

### 5. SSL Certificate Setup
```bash
sudo certbot --nginx -d leanaiconstruction.com -d www.leanaiconstruction.com
```

### 6. Verify Deployment
- Check PM2 status: `pm2 status`
- Check Nginx status: `sudo systemctl status nginx`
- Test application access

## Post-deployment Tasks
- [ ] Monitor application performance
- [ ] Set up alerting and notifications
- [ ] Test all application features
- [ ] Configure backup verification
- [ ] Document any issues or improvements

## Monitoring Commands
- PM2 status: `pm2 status`
- Application logs: `pm2 logs`
- Nginx status: `sudo systemctl status nginx`
- Monitor script: `/usr/local/bin/app-monitor.sh`
- Manual backup: `sudo /usr/local/bin/backup-apps.sh`

## Emergency Procedures
- Restart services: `sudo systemctl restart nginx && pm2 restart all`
- Check disk space: `df -h`
- Check memory usage: `free -h`
- View system logs: `journalctl -f`