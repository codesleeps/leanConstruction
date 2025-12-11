"""
Standalone test for demo account creation
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
import json
from pydantic import BaseModel, EmailStr
import hashlib
import hmac

# Mock database and models for testing
class MockUser:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockProject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockTask:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockWasteLog:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# Mock database session
class MockDB:
    def __init__(self):
        self.users = []
        self.projects = []
        self.tasks = []
        self.waste_logs = []

    def query(self, cls):
        if cls.__name__ == 'User':
            return MockQuery(self.users, cls)
        elif cls.__name__ == 'Project':
            return MockQuery(self.projects, cls)
        elif cls.__name__ == 'Task':
            return MockQuery(self.tasks, cls)
        elif cls.__name__ == 'WasteLog':
            return MockQuery(self.waste_logs, cls)
        return MockQuery([], cls)

    def add(self, obj):
        if isinstance(obj, MockUser):
            self.users.append(obj)
        elif isinstance(obj, MockProject):
            self.projects.append(obj)
        elif isinstance(obj, MockTask):
            self.tasks.append(obj)
        elif isinstance(obj, MockWasteLog):
            self.waste_logs.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

class MockQuery:
    def __init__(self, items, cls):
        self.items = items
        self.cls = cls

    def filter(self, *args):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items

    def offset(self, n):
        return MockQuery(self.items[n:], self.cls)

    def limit(self, n):
        return MockQuery(self.items[:n], self.cls)

    def count(self):
        return len(self.items)

# Global mock database
mock_db = MockDB()

def get_db():
    return mock_db

# Auth utilities
def get_password_hash(password: str) -> str:
    return f"hashed_{password}"

def authenticate_user(db, email: str, password: str):
    for user in db.users:
        if user.email == email and user.hashed_password == get_password_hash(password):
            return user
    return None

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: str
    role: str
    company_size: str
    construction_type: str
    phone_number: Optional[str] = None

# App setup
app = FastAPI(
    title="Demo Auth Test API",
    description="Test API for demo account creation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo account endpoints
@app.post("/api/auth/demo-account/create")
async def create_demo_account(
    account_type: str,
    background_tasks: BackgroundTasks,
    db: MockDB = Depends(get_db)
):
    """Create a demo account with pre-populated construction data"""

    # Validate account type
    valid_types = ["small", "medium", "enterprise"]
    if account_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid demo account type")

    # Generate demo credentials
    demo_email = f"demo-{account_type}-{secrets.token_hex(4)}@leanaiconstruction.com"
    demo_password = "Demo123!"

    # Check if demo account already exists
    existing_demo = None
    for user in db.users:
        if user.email == demo_email:
            existing_demo = user
            break

    if existing_demo:
        return {
            "demo_email": demo_email,
            "demo_password": demo_password,
            "message": "Demo account already exists",
            "login_url": "/login"
        }

    # Create demo user
    company_names = {
        "small": "ABC Home Builders",
        "medium": "Metro Construction Group",
        "enterprise": "Global Infrastructure Corp"
    }

    demo_user = MockUser(
        id=len(db.users) + 1,
        email=demo_email,
        hashed_password=get_password_hash(demo_password),
        full_name=f"Demo {account_type.title()} Manager",
        company=company_names[account_type],
        role="project_manager",
        company_size=account_type,
        construction_type="commercial",
        is_active=1,
        onboarding_step=4,
        demo_account=True,
        email_verified=True,
        trial_expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    # Create comprehensive demo data in background
    background_tasks.add_task(
        create_comprehensive_demo_data,
        demo_user.id,
        account_type,
        db
    )

    return {
        "demo_email": demo_email,
        "demo_password": demo_password,
        "message": f"Demo account created successfully for {account_type} contractor",
        "account_type": account_type,
        "login_url": "/login",
        "features": get_demo_features(account_type)
    }

@app.get("/api/auth/demo-accounts")
async def list_demo_accounts(db: MockDB = Depends(get_db)):
    """List available demo account types with detailed information"""

    return {
        "demo_accounts": [
            {
                "type": "small",
                "name": "Small Contractor",
                "description": "3-10 projects, perfect for small construction companies",
                "project_count": "5-8 projects",
                "sample_projects": [
                    "Residential Home Build",
                    "Small Office Renovation",
                    "Retail Store Construction"
                ],
                "features": [
                    "Basic waste tracking",
                    "Project management",
                    "Simple analytics",
                    "Cost monitoring",
                    "Timeline tracking"
                ],
                "savings_potential": "$50K - $150K per project",
                "demo_duration": "7 days full access"
            },
            {
                "type": "medium",
                "name": "Medium Builder",
                "description": "10-50 projects, ideal for growing construction businesses",
                "project_count": "15-25 projects",
                "sample_projects": [
                    "Commercial Building Phase 1",
                    "Shopping Center Development",
                    "Industrial Warehouse",
                    "Office Complex"
                ],
                "features": [
                    "Advanced waste detection",
                    "Team collaboration",
                    "Detailed reporting",
                    "Resource optimization",
                    "Predictive analytics"
                ],
                "savings_potential": "$200K - $500K per project",
                "demo_duration": "7 days full access"
            },
            {
                "type": "enterprise",
                "name": "Enterprise Client",
                "description": "50+ projects, designed for large construction corporations",
                "project_count": "60-100+ projects",
                "sample_projects": [
                    "Hospital Complex Construction",
                    "Airport Terminal Expansion",
                    "University Campus Development",
                    "Skyscraper Project",
                    "Infrastructure Network"
                ],
                "features": [
                    "AI-powered predictions",
                    "Custom integrations",
                    "White-label options",
                    "Advanced analytics",
                    "Multi-project oversight"
                ],
                "savings_potential": "$1M - $5M per project",
                "demo_duration": "7 days full access"
            }
        ]
    }

def get_demo_features(account_type: str) -> list:
    """Get features list for demo account type"""
    features_map = {
        "small": [
            "Basic waste tracking",
            "Project management",
            "Simple analytics",
            "Cost monitoring",
            "Timeline tracking"
        ],
        "medium": [
            "Advanced waste detection",
            "Team collaboration",
            "Detailed reporting",
            "Resource optimization",
            "Predictive analytics"
        ],
        "enterprise": [
            "AI-powered predictions",
            "Custom integrations",
            "White-label options",
            "Advanced analytics",
            "Multi-project oversight"
        ]
    }
    return features_map.get(account_type, [])

def create_comprehensive_demo_data(user_id: int, account_type: str, db: MockDB):
    """Create comprehensive demo data for construction projects"""

    # Demo project configurations based on account type
    project_configs = {
        "small": [
            {
                "name": "Residential Home Build",
                "description": "Modern 3-bedroom family home with sustainable features",
                "budget": 350000,
                "tasks": 12,
                "waste_logs": 4,
                "completion_rate": 0.75
            },
            {
                "name": "Small Office Renovation",
                "description": "Complete interior renovation of 2,000 sq ft office space",
                "budget": 85000,
                "tasks": 8,
                "waste_logs": 2,
                "completion_rate": 0.90
            },
            {
                "name": "Retail Store Construction",
                "description": "New construction of 1,500 sq ft retail space",
                "budget": 180000,
                "tasks": 15,
                "waste_logs": 3,
                "completion_rate": 0.60
            }
        ],
        "medium": [
            {
                "name": "Commercial Building Phase 1",
                "description": "First phase of 50,000 sq ft commercial development",
                "budget": 2500000,
                "tasks": 35,
                "waste_logs": 12,
                "completion_rate": 0.65
            },
            {
                "name": "Shopping Center Development",
                "description": "75,000 sq ft shopping center with anchor tenants",
                "budget": 4200000,
                "tasks": 55,
                "waste_logs": 18,
                "completion_rate": 0.45
            }
        ],
        "enterprise": [
            {
                "name": "Hospital Complex Construction",
                "description": "300-bed hospital with specialized medical facilities",
                "budget": 185000000,
                "tasks": 180,
                "waste_logs": 45,
                "completion_rate": 0.40
            },
            {
                "name": "Airport Terminal Expansion",
                "description": "Major expansion adding 500,000 sq ft to existing terminal",
                "budget": 320000000,
                "tasks": 220,
                "waste_logs": 60,
                "completion_rate": 0.35
            }
        ]
    }

    projects = project_configs.get(account_type, project_configs["small"])

    for i, project_config in enumerate(projects):
        # Create project
        demo_project = MockProject(
            id=len(db.projects) + 1,
            name=project_config["name"],
            description=project_config["description"],
            owner_id=user_id,
            budget=project_config["budget"],
            start_date=datetime.utcnow() - timedelta(days=30 * (i + 1)),
            end_date=datetime.utcnow() + timedelta(days=90 * (i + 1)),
            status="active"
        )
        db.add(demo_project)

        # Create demo tasks
        for j in range(project_config["tasks"]):
            task_statuses = ["pending", "in_progress", "completed"]
            task_priorities = ["low", "medium", "high"]

            # Calculate status based on completion rate
            status_index = 0
            if j < project_config["tasks"] * project_config["completion_rate"]:
                status_index = 2  # completed
            elif j < project_config["tasks"] * project_config["completion_rate"] * 0.7:
                status_index = 1  # in_progress

            task = MockTask(
                id=len(db.tasks) + 1,
                project_id=demo_project.id,
                name=f"Task {j+1} - {project_config['name']}",
                description=f"Demo task {j+1} for {project_config['name']}",
                status=task_statuses[status_index],
                priority=task_priorities[j % 3],
                estimated_hours=8.0 + (j * 0.5),
                actual_hours=7.5 + (j * 0.4) if status_index == 2 else None,
                assigned_to=user_id
            )
            db.add(task)

        # Create demo waste logs
        waste_types = [
            "defects", "waiting", "transportation", "overprocessing",
            "inventory", "motion", "overproduction", "skills"
        ]

        for k in range(project_config["waste_logs"]):
            waste_log = MockWasteLog(
                id=len(db.waste_logs) + 1,
                project_id=demo_project.id,
                waste_type=waste_types[k % len(waste_types)],
                description=f"Demo waste log {k+1} for {project_config['name']}",
                impact_cost=500.0 * (k + 1) * (10 if account_type == "enterprise" else 1),
                impact_time=2.0 + (k * 0.5),
                detected_at=datetime.utcnow() - timedelta(days=k * 2),
                resolved_at=datetime.utcnow() - timedelta(days=k) if k % 2 == 0 else None
            )
            db.add(waste_log)

    db.commit()
    print(f"Created comprehensive demo data for {account_type} account with {len(projects)} projects")

@app.get("/")
async def root():
    return {"message": "Demo Auth Test API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)