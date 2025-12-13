# Unattended Execution Configuration Guide

This guide provides configuration instructions for setting up unattended execution and YOLO Mode in Traycer for the Lean Construction AI platform.

## 📋 Overview

This configuration enables:
- **Unattended execution**: Automated deployment and execution without manual intervention
- **YOLO Mode**: Full automation of the software development lifecycle from planning to verification
- **CI/CD integration**: Seamless integration with existing GitHub Actions workflows

## 🔧 Environment Variables Configuration

### Root Environment Variables (.env)

Create or update the `.env` file in the root directory with these essential variables:

```env
# Core Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Deployment Automation
AUTO_DEPLOY=true
DEPLOY_BRANCH=main
DEPLOY_TRIGGER=push

# YOLO Mode Settings
YOLO_MODE=true
AUTO_VERIFY=true
AUTO_TEST=true
AUTO_DEPLOY=true
AUTO_NOTIFY=true

# Notification Settings
NOTIFICATION_EMAIL=admin@leanaiconstruction.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/XXX/XXX
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXX/XXX

# Monitoring
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=300
MONITORING_ENABLED=true

# Security
AUTO_ROLLBACK_ON_FAILURE=true
MAX_DEPLOYMENT_RETRIES=3
DEPLOYMENT_TIMEOUT=3600
```

### Backend Environment Variables (backend/.env)

Ensure these variables are set for production:

```env
# Database (use production-ready PostgreSQL)
DATABASE_URL=postgresql://username:password@prod-db:5432/lean_construction_prod

# Security
SECRET_KEY=your-production-secret-key-change-regularly
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Service
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=production@leanaiconstruction.com
SMTP_PASSWORD=app-specific-password
SMTP_USE_TLS=true
FROM_EMAIL=noreply@leanaiconstruction.com
FROM_NAME=Lean AI Construction

# Application URLs
FRONTEND_URL=https://leanaiconstruction.com
API_BASE_URL=https://api.leanaiconstruction.com
DASHBOARD_URL=https://app.leanaiconstruction.com

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://redis:6379/0

# Feature Flags
ENABLE_DEMO_ACCOUNTS=true
ENABLE_EMAIL_VERIFICATION=true
ENABLE_ONBOARDING_FLOW=true

# Payment Integration
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...

# Monitoring
SENTRY_DSN=your-production-sentry-dsn
HEALTH_CHECK_INTERVAL=30
```

## 🚀 YOLO Mode Configuration

YOLO Mode automates the entire software development lifecycle:

### YOLO Mode Features

1. **Automated Planning**: Auto-generates task lists and priorities
2. **Automated Implementation**: Executes code changes automatically
3. **Automated Testing**: Runs full test suite on every change
4. **Automated Verification**: Validates deployment success
5. **Automated Notification**: Sends alerts on success/failure

### Enabling YOLO Mode

Set these environment variables:

```env
# In .env file
YOLO_MODE=true
AUTO_VERIFY=true
AUTO_TEST=true
AUTO_DEPLOY=true
AUTO_NOTIFY=true
```

### YOLO Mode Workflow

When YOLO Mode is enabled, the system will:

1. **Detect changes** in the repository
2. **Analyze requirements** automatically
3. **Generate implementation plan**
4. **Execute changes** without manual intervention
5. **Run tests** automatically
6. **Deploy to staging** for verification
7. **Deploy to production** if tests pass
8. **Send notifications** to configured channels

## 🤖 CI/CD Pipeline Configuration

The existing GitHub Actions workflow has been enhanced for unattended execution.

### Current Workflow (.github/workflows/ci-cd.yml)

The workflow includes:
- Backend tests with PostgreSQL and Redis services
- Frontend tests and build
- Docker image building and pushing
- Production deployment

### Enhanced Features for Unattended Execution

1. **Automatic Deployment**: Triggers on push to main branch
2. **Parallel Testing**: Runs backend and frontend tests concurrently
3. **Artifact Management**: Stores test results and coverage reports
4. **Notification Integration**: Can be extended with Slack/Discord notifications

### Adding Notifications to CI/CD

Add this to your workflow:

```yaml
- name: Notify on success
  if: success()
  run: |
    curl -X POST -H 'Content-type: application/json' --data '{"text":"✅ Deployment successful: ${{ github.sha }}"}' ${{ secrets.SLACK_WEBHOOK_URL }}

- name: Notify on failure
  if: failure()
  run: |
    curl -X POST -H 'Content-type: application/json' --data '{"text":"❌ Deployment failed: ${{ github.sha }}"}' ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🔐 Security Configuration

### Required GitHub Secrets

Store these secrets in GitHub repository settings:

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token
- `SLACK_WEBHOOK_URL`: Slack incoming webhook URL (optional)
- `DISCORD_WEBHOOK_URL`: Discord webhook URL (optional)
- `AWS_ACCESS_KEY_ID`: AWS access key (if using AWS)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (if using AWS)
- `SENTRY_DSN`: Sentry DSN for error tracking

### Environment Variable Security

1. **Never commit `.env` files** to version control
2. **Use `.env.example`** as a template
3. **Rotate secrets regularly**
4. **Use different secrets** for development, staging, and production

## 📊 Monitoring and Logging

### Health Check Configuration

The health check script (`backend/lean-construction-healthcheck.sh`) verifies:
- Database connectivity
- API endpoint availability
- Background task queue status
- Service health

### Monitoring Setup

1. **Sentry**: For error tracking and monitoring
2. **Health Check Endpoint**: `GET /health` on backend API
3. **Celery Flower**: Task monitoring at `http://localhost:5555`

### Log Configuration

Set appropriate log levels:

```env
LOG_LEVEL=INFO  # For production
LOG_LEVEL=DEBUG  # For development
```

## 🎯 Deployment Strategies

### Blue-Green Deployment

1. Deploy new version to staging
2. Run smoke tests
3. Switch traffic from blue to green
4. Monitor for issues
5. Rollback if necessary

### Canary Deployment

1. Deploy to 10% of users
2. Monitor metrics
3. Gradually increase to 100%
4. Rollback if issues detected

## 🔄 Rollback Procedures

### Automatic Rollback

```env
AUTO_ROLLBACK_ON_FAILURE=true
MAX_DEPLOYMENT_RETRIES=3
```

### Manual Rollback

```bash
# Rollback to previous version
docker-compose down
docker-compose pull
docker-compose up -d
```

## 📚 Usage Examples

### Starting in Unattended Mode

```bash
# Set environment variables
export YOLO_MODE=true
export AUTO_DEPLOY=true

# Start the application
docker-compose up -d
```

### Running Tests Automatically

```bash
# Run full test suite
cd backend
pytest tests/ -v --cov=app

# Run with coverage
pytest tests/ -v --cov=app --cov-report=xml
```

### Deploying to Production

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using deployment script
./deploy/production-deployment.sh
```

## ⚠️ Troubleshooting

### Common Issues

1. **Environment variables not loaded**
   - Verify `.env` file exists
   - Check file permissions
   - Ensure variables are exported

2. **Deployment fails silently**
   - Check logs: `docker-compose logs`
   - Verify health check: `curl http://localhost:8000/health`
   - Check database connection

3. **Tests fail in CI but pass locally**
   - Ensure consistent environment variables
   - Verify database state
   - Check for missing dependencies

4. **Notifications not sent**
   - Verify webhook URLs are correct
   - Check network connectivity
   - Verify secrets are configured

### Debugging Commands

```bash
# Check environment variables
env | grep -i "env\|secret\|key"

# Check running containers
docker-compose ps

# View logs
docker-compose logs --tail=100

# Test health endpoint
curl http://localhost:8000/health

# Test database connection
cd backend
python -c "from app.database import engine; print('Database connected')"
```

## 📞 Support

For issues with unattended execution:

1. Check the logs first
2. Verify environment variables
3. Test health endpoints
4. Review CI/CD workflow runs
5. Contact support if needed

## 📝 Next Steps

1. [ ] Configure GitHub Secrets
2. [ ] Set up monitoring and notifications
3. [ ] Test unattended deployment workflow
4. [ ] Document rollback procedures
5. [ ] Implement canary deployment strategy

---

**Last Updated**: 2025-12-13
**Version**: 1.0
