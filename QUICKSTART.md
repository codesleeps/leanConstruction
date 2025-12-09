# Quick Start Guide

Get the Lean Construction AI platform running in 5 minutes!

## Prerequisites

- Docker Desktop installed
- 8GB RAM minimum
- 10GB free disk space

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd lean-construction-ai

# Copy environment file
cp .env.example .env

# (Optional) Edit .env with your settings
nano .env
```

## Step 2: Start Services (2 minutes)

```bash
# Build and start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps
```

## Step 3: Access Applications (1 minute)

Open your browser:

- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Task Monitor**: http://localhost:5555

## First Time Setup

### Create Your First User

Using the API docs at http://localhost:8000/docs:

1. Expand `POST /users/`
2. Click "Try it out"
3. Enter user details:
```json
{
  "email": "admin@example.com",
  "password": "securepassword123",
  "full_name": "Admin User",
  "company": "My Company",
  "role": "admin"
}
```
4. Click "Execute"

### Login and Get Token

1. Expand `POST /token`
2. Click "Try it out"
3. Enter credentials:
   - username: `admin@example.com`
   - password: `securepassword123`
4. Copy the `access_token` from response

### Create Your First Project

1. Click the 🔒 Authorize button at the top
2. Enter: `Bearer <your-access-token>`
3. Expand `POST /projects/`
4. Create a project:
```json
{
  "name": "Office Building Construction",
  "description": "Downtown office building project",
  "budget": 5000000,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

## Mobile App Setup (Optional)

```bash
cd mobile
npm install

# For iOS
npm run ios

# For Android
npm run android
```

## Verify Everything Works

### Check Backend Health

```bash
curl http://localhost:8000/health
```

### Check Celery Tasks

Visit http://localhost:5555 to see:
- Active workers
- Scheduled tasks
- Task history

### Check Database

```bash
docker exec -it <postgres-container-id> psql -U postgres -d leandb
\dt  # List tables
\q   # Quit
```

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
docker-compose down
```

### Reset Everything

```bash
docker-compose down -v  # Removes volumes (deletes data!)
docker-compose up -d
```

## Testing the Waste Detection

1. Create a project (see above)
2. Log some waste:

```bash
curl -X POST "http://localhost:8000/projects/1/waste/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "waste_type": "waiting",
    "description": "Materials delayed by 2 days",
    "impact_cost": 5000,
    "impact_time": 16
  }'
```

3. Check analytics:

```bash
curl "http://localhost:8000/projects/1/analytics/" \
  -H "Authorization: Bearer <your-token>"
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :3000  # or :8000, :5432, etc.

# Change ports in docker-compose.yml
```

### Services Not Starting

```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Error

```bash
# Wait for database to be ready
docker-compose logs db

# Restart backend after database is ready
docker-compose restart backend
```

### Out of Memory

```bash
# Increase Docker memory in Docker Desktop settings
# Recommended: 8GB minimum
```

## Next Steps

1. **Explore the API**: http://localhost:8000/docs
2. **Read the docs**: See README.md
3. **Set up Procore**: See integration docs
4. **Deploy to production**: See DEPLOYMENT.md
5. **Start Phase 2**: AI/ML model development

## Getting Help

- Check logs: `docker-compose logs -f`
- Review documentation: README.md
- Check GitHub issues
- Review API docs: http://localhost:8000/docs

## Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web dashboard |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive API docs |
| Flower | http://localhost:5555 | Task monitoring |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache/Queue |

## Environment Variables

Key variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@db/leandb
SECRET_KEY=change-this-in-production
CELERY_BROKER_URL=redis://redis:6379/0
```

## Success! 🎉

You now have:
- ✅ Backend API running
- ✅ Frontend dashboard running
- ✅ Database configured
- ✅ Celery workers processing tasks
- ✅ Task monitoring available
- ✅ Ready for development

Start building your Lean Construction AI platform!
