# Project Structure

Complete directory structure of the Lean Construction AI platform.

```
lean-construction-ai/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                    # GitHub Actions CI/CD pipeline
│
├── backend/                             # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # Main FastAPI application
│   │   ├── models.py                    # SQLAlchemy database models
│   │   ├── auth.py                      # Authentication & JWT
│   │   ├── celery_app.py                # Celery configuration
│   │   ├── integrations/                # External integrations
│   │   │   ├── __init__.py
│   │   │   └── procore.py               # Procore API client
│   │   └── tasks/                       # Celery tasks
│   │       ├── __init__.py
│   │       ├── data_ingestion.py        # Data ingestion tasks
│   │       └── analytics.py             # Analytics tasks
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_main.py                 # API tests
│   ├── database.py                      # Database configuration
│   ├── Dockerfile                       # Backend Docker image
│   ├── requirements.txt                 # Python dependencies
│   └── pytest.ini                       # Test configuration
│
├── frontend/                            # React.js Frontend
│   ├── src/
│   │   └── components/
│   │       └── Dashboard.js             # Dashboard component
│   ├── public/
│   ├── Dockerfile                       # Frontend Docker image
│   ├── nginx.conf                       # Nginx configuration
│   └── package.json                     # Node dependencies
│
├── mobile/                              # React Native Mobile App
│   ├── src/
│   │   ├── screens/
│   │   │   ├── LoginScreen.js           # Login screen
│   │   │   ├── DashboardScreen.js       # Dashboard screen
│   │   │   ├── ProjectsScreen.js        # Projects list
│   │   │   ├── ProjectDetailScreen.js   # Project details
│   │   │   ├── WasteLogScreen.js        # Waste logging
│   │   │   ├── CameraScreen.js          # Camera capture
│   │   │   └── ProfileScreen.js         # User profile
│   │   └── services/
│   │       └── api.js                   # API client
│   ├── android/                         # Android native code
│   ├── ios/                             # iOS native code
│   ├── App.js                           # Main app component
│   ├── index.js                         # App entry point
│   ├── app.json                         # App configuration
│   ├── babel.config.js                  # Babel configuration
│   ├── metro.config.js                  # Metro bundler config
│   ├── package.json                     # Dependencies
│   └── README.md                        # Mobile app docs
│
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── docker-compose.yml                   # Development environment
├── docker-compose.prod.yml              # Production environment
├── setup.sh                             # Setup script
│
├── README.md                            # Main documentation
├── QUICKSTART.md                        # Quick start guide
├── DEPLOYMENT.md                        # Deployment guide
├── PLAN.MD                              # Complete project plan
├── TODO.md                              # Task tracking
├── COMPLETED_PHASE1.md                  # Phase 1 summary
├── PROJECT_STRUCTURE.md                 # This file
└── competition.html                     # Competition info
```

## Directory Descriptions

### Backend (`/backend`)

**Purpose**: FastAPI-based REST API server with AI/ML capabilities

**Key Files**:
- `main.py`: API endpoints, request handling
- `models.py`: Database schema (User, Project, Task, WasteLog)
- `auth.py`: JWT authentication, password hashing
- `celery_app.py`: Background task configuration
- `database.py`: SQLAlchemy setup

**Integrations** (`/backend/app/integrations`):
- `procore.py`: Procore API client for project management data

**Tasks** (`/backend/app/tasks`):
- `data_ingestion.py`: Automated data collection and processing
- `analytics.py`: Weekly reports and value stream mapping

**Tests** (`/backend/tests`):
- Unit tests for API endpoints
- Integration tests for database operations

### Frontend (`/frontend`)

**Purpose**: React.js web dashboard for project monitoring

**Key Features**:
- Real-time project metrics
- Waste detection visualization
- Task management interface
- Analytics dashboards

**Deployment**:
- Multi-stage Docker build
- Nginx for production serving
- Optimized static assets

### Mobile (`/mobile`)

**Purpose**: React Native mobile app for field operations

**Screens**:
1. **Login**: User authentication
2. **Dashboard**: Real-time metrics and charts
3. **Projects**: Project list and search
4. **Project Detail**: Detailed project information
5. **Waste Log**: Log waste incidents (DOWNTIME)
6. **Camera**: Site photo capture
7. **Profile**: User settings and logout

**Services**:
- API client with token management
- Offline data caching (ready)
- Push notifications (ready)

### Configuration Files

**Docker**:
- `docker-compose.yml`: Development with hot-reload
- `docker-compose.prod.yml`: Production with optimizations
- `Dockerfile` (backend): Python 3.11 with dependencies
- `Dockerfile` (frontend): Multi-stage with Nginx

**CI/CD**:
- `.github/workflows/ci-cd.yml`: Automated testing and deployment

**Environment**:
- `.env.example`: Template for environment variables
- `.gitignore`: Files to exclude from version control

### Documentation

**User Guides**:
- `README.md`: Complete project overview
- `QUICKSTART.md`: 5-minute setup guide
- `DEPLOYMENT.md`: Production deployment

**Development**:
- `PLAN.MD`: Full development roadmap
- `TODO.md`: Task tracking with phases
- `COMPLETED_PHASE1.md`: Phase 1 achievements
- `PROJECT_STRUCTURE.md`: This file

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │   Backend    │  │  Mobile App  │ │
│  │   (React)    │  │  (FastAPI)   │  │(React Native)│ │
│  │  Port 3000   │  │  Port 8000   │  │   External   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                  │         │
│         └─────────────────┼──────────────────┘         │
│                           │                            │
│  ┌────────────────────────┼────────────────────────┐  │
│  │                        │                        │  │
│  │  ┌─────────────┐  ┌────▼─────┐  ┌───────────┐  │  │
│  │  │ PostgreSQL  │  │  Redis   │  │  Celery   │  │  │
│  │  │ Port 5432   │  │Port 6379 │  │  Worker   │  │  │
│  │  └─────────────┘  └──────────┘  └─────┬─────┘  │  │
│  │                                        │        │  │
│  │  ┌─────────────┐  ┌──────────┐  ┌────▼─────┐  │  │
│  │  │Celery Beat  │  │  Flower  │  │  Logs    │  │  │
│  │  │ Scheduler   │  │Port 5555 │  │          │  │  │
│  │  └─────────────┘  └──────────┘  └──────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Request Flow
```
Mobile/Web → Backend API → Database
                ↓
            Celery Task (async)
                ↓
            Redis Queue
                ↓
            Celery Worker
                ↓
            Database Update
```

### 2. Automated Task Flow
```
Celery Beat (Scheduler)
    ↓
Schedule Task (cron)
    ↓
Redis Queue
    ↓
Celery Worker
    ↓
Data Processing
    ↓
Database Update
    ↓
Notification (optional)
```

### 3. Integration Flow
```
External System (Procore)
    ↓
API Client (backend/integrations)
    ↓
Data Transformation
    ↓
Celery Task (async)
    ↓
Database Storage
    ↓
Analytics Processing
```

## Database Schema

### Core Tables

**users**
- id, email, hashed_password
- full_name, company, role
- created_at, is_active

**projects**
- id, name, description
- owner_id (FK → users)
- status, budget
- start_date, end_date

**tasks**
- id, project_id (FK → projects)
- name, description, status
- priority, assigned_to
- estimated_hours, actual_hours

**waste_logs**
- id, project_id (FK → projects)
- waste_type, description
- impact_cost, impact_time
- detected_at, resolved_at

## API Endpoints

### Authentication
- `POST /token` - Login
- `POST /users/` - Register
- `GET /users/me` - Current user

### Projects
- `GET /projects/` - List projects
- `POST /projects/` - Create project
- `GET /projects/{id}/analytics/` - Project analytics

### Tasks
- `POST /projects/{id}/tasks/` - Create task

### Waste Logging
- `POST /projects/{id}/waste/` - Log waste

### Integrations
- `POST /integrations/procore/auth` - Authenticate
- `POST /integrations/procore/sync/{id}` - Sync project
- `GET /integrations/procore/projects` - List projects

## Celery Tasks

### Scheduled Tasks

**Morning Health Check** (6 AM daily)
- Task: `morning_project_health_check`
- Purpose: Analyze overnight data
- Output: Health status reports

**Waste Detection** (Every 30 min)
- Task: `detect_waste_patterns`
- Purpose: Continuous monitoring
- Output: Waste indicators

**Progress Tracking** (Every 15 min)
- Task: `update_project_progress`
- Purpose: Update metrics
- Output: Progress data

**Weekly Analysis** (Monday 7 AM)
- Task: `weekly_strategic_analysis`
- Purpose: Strategic review
- Output: Recommendations

### On-Demand Tasks

- `ingest_external_data` - Process external data
- `generate_value_stream_map` - Create VSM

## Technology Stack

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Celery
- Redis
- PostgreSQL

### Frontend
- React 18
- Material-UI
- Axios
- Recharts

### Mobile
- React Native 0.72
- React Navigation
- React Native Paper
- Axios

### DevOps
- Docker
- Docker Compose
- GitHub Actions
- Nginx

### AI/ML (Phase 2)
- PyTorch
- Transformers
- OpenCV
- scikit-learn
- XGBoost

## File Sizes (Approximate)

- Backend code: ~2,500 lines
- Frontend code: ~500 lines
- Mobile code: ~1,000 lines
- Configuration: ~500 lines
- Documentation: ~2,000 lines
- **Total: ~6,500 lines**

## Next Steps

See `TODO.md` for Phase 2 tasks:
- Computer vision models
- Waste detection algorithms
- Predictive analytics
- Advanced reporting
