# Deployment Guide

This guide covers deploying the Lean Construction AI platform to production environments.

## Prerequisites

- Docker & Docker Compose
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)
- Cloud provider account (AWS/Azure/GCP)

## Environment Variables

Create a `.env` file with production values:

```env
# Database
POSTGRES_DB=leandb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>

# Security
SECRET_KEY=<generate-strong-random-key>

# Docker
DOCKER_USERNAME=<your-dockerhub-username>

# Procore (if using)
PROCORE_CLIENT_ID=<your-client-id>
PROCORE_CLIENT_SECRET=<your-client-secret>
```

## Deployment Options

### Option 1: Docker Compose (Simple)

Best for: Small to medium deployments, single server

```bash
# Build and push images
docker-compose build
docker login
docker-compose push

# On production server
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECR repositories**
```bash
aws ecr create-repository --repository-name lean-construction-backend
aws ecr create-repository --repository-name lean-construction-frontend
```

2. **Build and push images**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag lean-construction-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lean-construction-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lean-construction-backend:latest
```

3. **Create ECS cluster**
```bash
aws ecs create-cluster --cluster-name lean-construction-cluster
```

4. **Create task definitions** (see `aws/ecs-task-definition.json`)

5. **Create services**
```bash
aws ecs create-service \
  --cluster lean-construction-cluster \
  --service-name backend-service \
  --task-definition backend-task \
  --desired-count 2 \
  --launch-type FARGATE
```

#### Using AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize application**
```bash
eb init -p docker lean-construction-ai
```

3. **Create environment**
```bash
eb create production-env
```

4. **Deploy**
```bash
eb deploy
```

### Option 3: Azure Deployment

#### Using Azure Container Instances

1. **Create resource group**
```bash
az group create --name lean-construction-rg --location eastus
```

2. **Create container registry**
```bash
az acr create --resource-group lean-construction-rg --name leanconstructionacr --sku Basic
```

3. **Build and push images**
```bash
az acr build --registry leanconstructionacr --image backend:latest ./backend
az acr build --registry leanconstructionacr --image frontend:latest ./frontend
```

4. **Deploy containers**
```bash
az container create \
  --resource-group lean-construction-rg \
  --name backend \
  --image leanconstructionacr.azurecr.io/backend:latest \
  --dns-name-label lean-backend \
  --ports 8000
```

### Option 4: GCP Deployment

#### Using Google Cloud Run

1. **Build and push to Container Registry**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/frontend ./frontend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy backend \
  --image gcr.io/PROJECT_ID/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy frontend \
  --image gcr.io/PROJECT_ID/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Database Setup

### PostgreSQL on RDS (AWS)

```bash
aws rds create-db-instance \
  --db-instance-identifier lean-construction-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20
```

### Azure Database for PostgreSQL

```bash
az postgres server create \
  --resource-group lean-construction-rg \
  --name lean-construction-db \
  --location eastus \
  --admin-user postgres \
  --admin-password <password> \
  --sku-name B_Gen5_1
```

## SSL/TLS Setup

### Using Let's Encrypt with Nginx

1. **Install Certbot**
```bash
apt-get update
apt-get install certbot python3-certbot-nginx
```

2. **Obtain certificate**
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal**
```bash
certbot renew --dry-run
```

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/lean-construction

# Set retention
aws logs put-retention-policy \
  --log-group-name /ecs/lean-construction \
  --retention-in-days 30
```

### Application Insights (Azure)

```bash
az monitor app-insights component create \
  --app lean-construction-insights \
  --location eastus \
  --resource-group lean-construction-rg
```

## Scaling

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale celery_worker=5
```

**Kubernetes:**
```bash
kubectl scale deployment backend --replicas=3
kubectl scale deployment celery-worker --replicas=5
```

### Auto-scaling (AWS ECS)

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/lean-construction-cluster/backend-service \
  --min-capacity 2 \
  --max-capacity 10
```

## Backup Strategy

### Database Backups

**Automated (AWS RDS):**
```bash
aws rds modify-db-instance \
  --db-instance-identifier lean-construction-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

**Manual:**
```bash
# Backup
docker exec postgres pg_dump -U postgres leandb > backup.sql

# Restore
docker exec -i postgres psql -U postgres leandb < backup.sql
```

## Health Checks

Add health check endpoints:

```python
# backend/app/main.py
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

Configure load balancer health checks to use `/health` endpoint.

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up VPC/network isolation
- [ ] Enable database encryption
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Implement backup strategy
- [ ] Set up monitoring alerts

## Rollback Procedure

### Docker Compose

```bash
# Tag current version
docker tag backend:latest backend:v1.0.0

# Rollback
docker-compose down
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
kubectl rollout undo deployment/backend
```

### AWS ECS

```bash
aws ecs update-service \
  --cluster lean-construction-cluster \
  --service backend-service \
  --task-definition backend-task:1
```

## Troubleshooting

### Check logs

```bash
# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend

# AWS ECS
aws logs tail /ecs/lean-construction --follow
```

### Database connection issues

```bash
# Test connection
docker exec backend python -c "from app.database import engine; print(engine.connect())"
```

### Performance issues

```bash
# Check resource usage
docker stats

# Scale up
docker-compose -f docker-compose.prod.yml up -d --scale backend=5
```

## Support

For deployment issues:
- Check logs first
- Review environment variables
- Verify network connectivity
- Check resource limits
- Consult cloud provider documentation
