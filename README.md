# Lean Construction AI - Automated Consultancy Platform

An AI-powered application that automates Lean construction consultancy tasks, providing 24/7 insights, waste detection, and process optimization for construction projects.

## 🚀 Features

- **Real-time Project Monitoring**: 24/7 analysis of construction processes
- **Automated Waste Detection**: Identifies the 8 wastes (DOWNTIME) in construction
- **Predictive Analytics**: Forecasts schedule delays and cost overruns
- **Project Management Integration**: Syncs with Procore and other PM tools
- **Mobile App**: Field data collection and real-time notifications
- **Automated Reporting**: Daily health checks and weekly strategic analysis

## 🏗️ Architecture

```
├── backend/          # FastAPI backend with AI/ML models
├── frontend/         # React.js web dashboard
├── mobile/           # React Native mobile app
├── .github/          # CI/CD workflows
└── docker-compose.yml
```

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Git

## 🔧 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd lean-construction-ai
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@db/leandb

# Security
SECRET_KEY=your-secret-key-change-in-production

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Procore Integration (optional)
PROCORE_CLIENT_ID=your-procore-client-id
PROCORE_CLIENT_SECRET=your-procore-client-secret
PROCORE_ACCESS_TOKEN=your-access-token
```

### 3. Start the application

```bash
docker-compose up -d
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000
- **Celery Flower**: http://localhost:5555 (task monitoring)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Access the application

- Web Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Task Monitor: http://localhost:5555

## 📱 Mobile App Setup

### iOS

```bash
cd mobile
npm install
cd ios && pod install && cd ..
npm run ios
```

### Android

```bash
cd mobile
npm install
npm run android
```

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows for:
- Automated testing (backend & frontend)
- Code linting and quality checks
- Docker image building and pushing
- Deployment automation

### Required GitHub Secrets

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password/token

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm install
npm test
```

## 📊 Celery Tasks

The application runs several automated tasks:

- **Morning Health Check** (6 AM daily): Analyzes overnight data
- **Waste Detection** (Every 30 min): Continuous monitoring
- **Progress Tracking** (Every 15 min): Updates project metrics
- **Weekly Analysis** (Monday 7 AM): Strategic recommendations

Monitor tasks at: http://localhost:5555

## 🔌 Integrations

### Procore Integration

1. Register your app at [Procore Developer Portal](https://developers.procore.com)
2. Add credentials to `.env` file
3. Authenticate via API: `POST /integrations/procore/auth`
4. Sync projects: `POST /integrations/procore/sync/{project_id}`

### Adding New Integrations

Create a new integration module in `backend/app/integrations/`:

```python
# backend/app/integrations/your_tool.py
class YourToolClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def sync_project_data(self, project_id):
        # Implementation
        pass
```

## 🗄️ Database Schema

Key models:
- **User**: Authentication and user management
- **Project**: Construction project details
- **Task**: Project tasks and activities
- **WasteLog**: Detected waste incidents (DOWNTIME)

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Start Celery Worker (local)

```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Start Celery Beat (local)

```bash
cd backend
celery -A app.celery_app beat --loglevel=info
```

## 📈 Monitoring & Logging

- **Celery Flower**: Task monitoring at http://localhost:5555
- **API Logs**: Check Docker logs with `docker-compose logs backend`
- **Database**: Connect to PostgreSQL at localhost:5432

## 🔐 Security

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Regular security audits

## 🚢 Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

The application is ready for deployment on:
- AWS (ECS, EKS, or Elastic Beanstalk)
- Azure (Container Instances or AKS)
- GCP (Cloud Run or GKE)

## 📝 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Add your license here]

## 📞 Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]

## 🗺️ Roadmap

See [TODO.md](TODO.md) for the complete development roadmap.

### Phase 1 (Current) ✅
- ✅ CI/CD Pipeline
- ✅ Data Ingestion System
- ✅ Mobile App Framework
- ✅ Procore Integration

### Phase 2 (Next)
- Computer Vision Models
- Waste Detection Algorithms
- Predictive Analytics
- Automated Reporting

### Phase 3
- Advanced Lean Tools
- NLP Models
- Resource Optimization
- Real-time Alerting

### Phase 4
- Model Fine-tuning
- Advanced Analytics
- Industry Customizations
- Commercial Launch
