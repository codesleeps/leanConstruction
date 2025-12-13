# YOLO Mode Setup Guide

This guide provides detailed instructions for configuring and using YOLO Mode in Traycer for the Lean Construction AI platform.

## 🎯 What is YOLO Mode?

**YOLO Mode** (You Only Live Once) is an advanced automation feature that enables complete unattended execution of the software development lifecycle. When enabled, YOLO Mode automates:

1. **Planning**: Automatic task analysis and prioritization
2. **Implementation**: Code changes without manual intervention
3. **Testing**: Full test suite execution
4. **Verification**: Deployment validation
5. **Notification**: Alerts on success/failure

## 🚀 Enabling YOLO Mode

### Prerequisite Configuration

Before enabling YOLO Mode, ensure these prerequisites are met:

1. ✅ GitHub repository with proper access
2. ✅ Docker Hub or container registry account
3. ✅ Production environment configured
4. ✅ Environment variables set
5. ✅ CI/CD pipeline working

### Step 1: Configure Environment Variables

Set these variables in your `.env` file:

```env
# Enable YOLO Mode
YOLO_MODE=true

# Automate all processes
AUTO_DEPLOY=true
AUTO_TEST=true
AUTO_VERIFY=true
AUTO_NOTIFY=true

# Deployment settings
AUTO_DEPLOY_BRANCH=main
DEPLOY_TRIGGER=push
MAX_DEPLOYMENT_RETRIES=3
DEPLOYMENT_TIMEOUT=3600
AUTO_ROLLBACK_ON_FAILURE=true

# Notifications
NOTIFICATION_EMAIL=admin@leanaiconstruction.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/XXX/XXX
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXX/XXX
```

### Step 2: Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. **DOCKER_USERNAME**: Your Docker Hub username
2. **DOCKER_PASSWORD**: Your Docker Hub password or access token
3. **SLACK_WEBHOOK_URL**: (Optional) Slack incoming webhook URL
4. **DISCORD_WEBHOOK_URL**: (Optional) Discord webhook URL
5. **AWS_ACCESS_KEY_ID**: (Optional) AWS access key
6. **AWS_SECRET_ACCESS_KEY**: (Optional) AWS secret key

### Step 3: Update CI/CD Workflow

The workflow has been enhanced with YOLO Mode support:

```yaml
# .github/workflows/ci-cd.yml

deploy:
  runs-on: ubuntu-latest
  needs: docker-build
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  
  steps:
  - uses: actions/checkout@v3
  
  - name: Set up environment
    run: |
      echo "YOLO_MODE=true" >> $GITHUB_ENV
      echo "AUTO_DEPLOY=true" >> $GITHUB_ENV
      echo "AUTO_VERIFY=true" >> $GITHUB_ENV
      echo "AUTO_NOTIFY=true" >> $GITHUB_ENV
  
  - name: Deploy to production
    run: |
      echo "🚀 Starting production deployment for commit ${{ github.sha }}"
      # Deployment commands here
  
  - name: Verify deployment
    if: env.YOLO_MODE == 'true'
    run: |
      echo "🔍 Verifying deployment..."
      curl -v http://api.leanaiconstruction.com/health
  
  - name: Notify on success
    if: success() && env.AUTO_NOTIFY == 'true'
    run: |
      # Send notifications to Slack/Discord
  
  - name: Notify on failure
    if: failure() && env.AUTO_NOTIFY == 'true'
    run: |
      # Send failure notifications
```

## 🔄 YOLO Mode Workflow

### How YOLO Mode Works

1. **Trigger**: Push to main branch
2. **Build**: Docker images are built and pushed
3. **Test**: All tests run automatically
4. **Deploy**: Production deployment begins
5. **Verify**: Health checks validate deployment
6. **Notify**: Success/failure alerts are sent

### Visual Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    YOLO Mode Workflow                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  Code Change │───▶│  Build      │───▶│  Test       │───▶│
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│              │                              │              │
│              ▼                              ▼              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 Deployment Phase                   │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────┐  │  │
│  │  │  Deploy      │───▶│  Verify     │───▶│  Notify │  │  │
│  │  └─────────────┘    └─────────────┘    └─────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Configuration Options

### YOLO Mode Flags

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `YOLO_MODE` | Enable/disable YOLO Mode | `false` | `true` |
| `AUTO_DEPLOY` | Auto-deploy to production | `false` | `true` |
| `AUTO_TEST` | Run tests automatically | `false` | `true` |
| `AUTO_VERIFY` | Verify deployment | `false` | `true` |
| `AUTO_NOTIFY` | Send notifications | `false` | `true` |
| `AUTO_ROLLBACK` | Auto-rollback on failure | `false` | `true` |

### Deployment Settings

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `AUTO_DEPLOY_BRANCH` | Branch to trigger deployment | `main` | `main` |
| `DEPLOY_TRIGGER` | Event to trigger deployment | `push` | `push` |
| `MAX_DEPLOYMENT_RETRIES` | Max retry attempts | `3` | `3` |
| `DEPLOYMENT_TIMEOUT` | Deployment timeout (seconds) | `3600` | `3600` |

### Notification Settings

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `NOTIFICATION_EMAIL` | Email for notifications | `` | `admin@yourdomain.com` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | `` | Your Slack webhook |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | `` | Your Discord webhook |

## 📊 Monitoring and Verification

### Health Check Endpoint

After deployment, YOLO Mode verifies the deployment using the health check endpoint:

```bash
curl -v http://api.leanaiconstruction.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "api": "running",
    "celery": "running",
    "redis": "connected"
  },
  "version": "1.0.0",
  "commit": "abc123"
}
```

### Monitoring Tools

1. **Sentry**: Error tracking and monitoring
2. **Health Check Script**: `backend/lean-construction-healthcheck.sh`
3. **Celery Flower**: Task monitoring at `http://localhost:5555`
4. **Docker Logs**: `docker-compose logs`

## 🔐 Security Considerations

### Best Practices

1. **Never commit `.env` files** to version control
2. **Use different secrets** for development, staging, and production
3. **Rotate secrets regularly** (every 90 days)
4. **Enable two-factor authentication** on all accounts
5. **Use least privilege** for deployment accounts

### Security Checklist

- [ ] GitHub Secrets configured
- [ ] Docker Hub access token (not password)
- [ ] Different secrets for each environment
- [ ] Regular secret rotation schedule
- [ ] Monitoring for suspicious activity
- [ ] Backup and recovery procedures

## ⚠️ Troubleshooting

### Common Issues and Solutions

#### Issue 1: Deployment fails silently

**Solution:**
```bash
# Check logs
docker-compose logs --tail=100

# Verify health endpoint
curl http://localhost:8000/health

# Check database connection
cd backend
python -c "from app.database import engine; print('Database connected')"
```

#### Issue 2: Tests fail in CI but pass locally

**Solution:**
```bash
# Ensure consistent environment
cat .env

# Verify database state
psql -h localhost -U postgres -c "\l"

# Check for missing dependencies
pip install -r requirements.txt
```

#### Issue 3: Notifications not sent

**Solution:**
```bash
# Verify webhook URLs
cat .env | grep WEBHOOK

# Test Slack notification
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test notification"}' \
  ${{ secrets.SLACK_WEBHOOK_URL }}
```

#### Issue 4: YOLO Mode not triggering

**Solution:**
```bash
# Check environment variables
env | grep YOLO

# Verify workflow file
cat .github/workflows/ci-cd.yml | grep YOLO_MODE
```

## 📚 Usage Examples

### Example 1: Basic YOLO Mode Setup

```bash
# Clone repository
git clone https://github.com/yourorg/lean-construction-ai.git
cd lean-construction-ai

# Create .env file
cp .env.example .env

# Edit .env to enable YOLO Mode
nano .env

# Add GitHub Secrets
# Go to GitHub → Settings → Secrets → Actions
# Add DOCKER_USERNAME, DOCKER_PASSWORD, etc.

# Push changes
git add .
git commit -m "Enable YOLO Mode"
git push origin main
```

### Example 2: Testing YOLO Mode Locally

```bash
# Set environment variables
export YOLO_MODE=true
export AUTO_DEPLOY=false  # Disable for local testing
export AUTO_TEST=true
export AUTO_VERIFY=true

# Run tests
cd backend
pytest tests/ -v

# Check coverage
pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Example 3: Manual Deployment with YOLO Verification

```bash
# Build and push Docker images
docker-compose build
docker-compose push

# Deploy manually
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment (YOLO Mode style)
curl -v http://api.leanaiconstruction.com/health

# Check logs
docker-compose logs --tail=50
```

## 🎯 Advanced Configuration

### Custom Deployment Scripts

Create custom deployment scripts in the `deploy/` directory:

```bash
# deploy/custom-deployment.sh
#!/bin/bash

# Custom deployment logic
echo "🚀 Custom deployment started"

# Your custom deployment commands here
docker-compose -f docker-compose.prod.yml up -d

# Verify
echo "🔍 Verifying deployment..."
curl -v http://api.leanaiconstruction.com/health

# Notify
echo "🎉 Deployment complete"
```

### Canary Deployment Strategy

```yaml
# .github/workflows/ci-cd.yml
deploy:
  runs-on: ubuntu-latest
  needs: docker-build
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  
  steps:
  - uses: actions/checkout@v3
  
  - name: Canary Deployment (10% traffic)
    run: |
      echo "🚀 Deploying to canary environment (10% traffic)"
      # Deploy to canary environment
      kubectl apply -f k8s/canary-deployment.yaml
      
      # Wait for verification
      sleep 300
      
      # Verify canary
      curl -v http://canary-api.leanaiconstruction.com/health
      
      # Promote to production if successful
      echo "✅ Canary verification passed, promoting to production"
      kubectl apply -f k8s/production-deployment.yaml
```

## 📞 Support and Resources

### Support Channels

- **GitHub Issues**: [https://github.com/yourorg/lean-construction-ai/issues](https://github.com/yourorg/lean-construction-ai/issues)
- **Slack Community**: [invite link](https://slack.leanaiconstruction.com)
- **Discord Server**: [invite link](https://discord.gg/leanaiconstruction)

### Documentation

- **Main Documentation**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Unattended Execution**: [UNATTENDED_EXECUTION_CONFIG.md](UNATTENDED_EXECUTION_CONFIG.md)
- **CI/CD Pipeline**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)

### FAQ

**Q: What happens if deployment fails?**
A: If `AUTO_ROLLBACK_ON_FAILURE=true`, the system will automatically rollback to the previous version. You'll also receive a notification.

**Q: Can I disable specific YOLO Mode features?**
A: Yes, set individual flags to `false`:
- `AUTO_DEPLOY=false` - Disable auto-deployment
- `AUTO_TEST=false` - Disable auto-testing
- `AUTO_NOTIFY=false` - Disable notifications

**Q: How do I monitor YOLO Mode deployments?**
A: Check GitHub Actions workflow runs, and set up monitoring with Sentry or other tools.

**Q: Can I use YOLO Mode with other CI/CD tools?**
A: Currently YOLO Mode is optimized for GitHub Actions. Custom integration may be needed for other tools.

## 📝 Next Steps

1. [ ] Configure GitHub Secrets
2. [ ] Test YOLO Mode in staging environment
3. [ ] Set up monitoring and alerts
4. [ ] Document rollback procedures
5. [ ] Implement canary deployment strategy
6. [ ] Enable YOLO Mode for production

---

**Last Updated**: 2025-12-13
**Version**: 1.0
