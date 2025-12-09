from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .database import SessionLocal, engine
from .models import Base, User, Project, Task, WasteLog
from .auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from .integrations.procore import ProcoreClient, analyze_procore_data_for_waste
from .tasks.data_ingestion import ingest_external_data
from .api.ml_routes import router as ml_router
from pydantic import BaseModel
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lean Construction AI API",
    description="AI-powered construction analytics platform with computer vision, waste detection, and predictive forecasting",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ML API routes
app.include_router(ml_router, prefix="/api/v1")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    company: str
    role: str

class ProjectCreate(BaseModel):
    name: str
    description: str
    budget: float
    start_date: str
    end_date: str

class TaskCreate(BaseModel):
    name: str
    description: str
    priority: str
    estimated_hours: float

class WasteLogCreate(BaseModel):
    waste_type: str
    description: str
    impact_cost: float
    impact_time: float

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        company=user.company,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully", "user_id": db_user.id}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company": current_user.company,
        "role": current_user.role
    }

@app.post("/projects/", response_model=dict)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=current_user.id,
        budget=project.budget,
        start_date=project.start_date,
        end_date=project.end_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"message": "Project created successfully", "project_id": db_project.id}

@app.get("/projects/")
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).offset(skip).limit(limit).all()
    return projects

@app.post("/projects/{project_id}/tasks/", response_model=dict)
def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_task = Task(
        project_id=project_id,
        name=task.name,
        description=task.description,
        priority=task.priority,
        estimated_hours=task.estimated_hours
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"message": "Task created successfully", "task_id": db_task.id}

@app.post("/projects/{project_id}/waste/", response_model=dict)
def log_waste(
    project_id: int,
    waste: WasteLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_waste = WasteLog(
        project_id=project_id,
        waste_type=waste.waste_type,
        description=waste.description,
        impact_cost=waste.impact_cost,
        impact_time=waste.impact_time
    )
    db.add(db_waste)
    db.commit()
    db.refresh(db_waste)
    return {"message": "Waste logged successfully", "waste_id": db_waste.id}

@app.get("/projects/{project_id}/analytics/")
def get_project_analytics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Basic analytics
    total_tasks = db.query(Task).filter(Task.project_id == project_id).count()
    completed_tasks = db.query(Task).filter(Task.project_id == project_id, Task.status == "completed").count()
    total_waste_cost = db.query(WasteLog).filter(WasteLog.project_id == project_id).with_entities(WasteLog.impact_cost).all()
    total_waste_cost = sum(cost[0] for cost in total_waste_cost) if total_waste_cost else 0
    
    return {
        "project_name": project.name,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "total_waste_cost": total_waste_cost,
        "budget_remaining": project.budget - total_waste_cost
    }

# Procore Integration Endpoints
class ProcoreAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class ProcoreSyncRequest(BaseModel):
    procore_project_id: int
    company_id: int

@app.post("/integrations/procore/auth")
async def procore_authenticate(
    auth_data: ProcoreAuthRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Authenticate with Procore and store access token"""
    client_id = os.getenv("PROCORE_CLIENT_ID")
    client_secret = os.getenv("PROCORE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Procore credentials not configured")
    
    try:
        client = ProcoreClient(client_id, client_secret)
        token_data = client.authenticate(auth_data.redirect_uri, auth_data.code)
        
        # Store token securely (in production, encrypt and store in database)
        return {
            "message": "Successfully authenticated with Procore",
            "expires_in": token_data.get("expires_in")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/integrations/procore/sync/{project_id}")
async def sync_procore_project(
    project_id: int,
    sync_data: ProcoreSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sync data from Procore for a specific project"""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get Procore credentials
    client_id = os.getenv("PROCORE_CLIENT_ID")
    client_secret = os.getenv("PROCORE_CLIENT_SECRET")
    access_token = os.getenv("PROCORE_ACCESS_TOKEN")  # In production, retrieve from secure storage
    
    if not all([client_id, client_secret, access_token]):
        raise HTTPException(status_code=500, detail="Procore integration not configured")
    
    try:
        # Initialize Procore client
        client = ProcoreClient(client_id, client_secret, access_token)
        
        # Sync project data
        procore_data = client.sync_project_data(sync_data.procore_project_id)
        
        # Analyze for waste
        waste_analysis = analyze_procore_data_for_waste(procore_data)
        
        # Queue async processing
        task = ingest_external_data.delay("procore", project_id, procore_data)
        
        return {
            "message": "Procore sync initiated",
            "task_id": task.id,
            "waste_analysis": waste_analysis,
            "data_summary": {
                "activities": len(procore_data.get("schedule_activities", [])),
                "rfis": len(procore_data.get("rfis", [])),
                "change_orders": len(procore_data.get("change_orders", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.get("/integrations/procore/projects")
async def list_procore_projects(
    company_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """List all Procore projects for a company"""
    client_id = os.getenv("PROCORE_CLIENT_ID")
    client_secret = os.getenv("PROCORE_CLIENT_SECRET")
    access_token = os.getenv("PROCORE_ACCESS_TOKEN")
    
    if not all([client_id, client_secret, access_token]):
        raise HTTPException(status_code=500, detail="Procore integration not configured")
    
    try:
        client = ProcoreClient(client_id, client_secret, access_token)
        projects = client.get_projects(company_id)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")
