"""
Customer Onboarding API Routes

Handles user registration, onboarding flow, demo accounts, and email notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json
import secrets
import string
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import User, Project, Task, WasteLog, OnboardingEvent, EmailNotification
from ..auth import get_password_hash, get_current_active_user

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for onboarding
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    company: str
    role: str
    company_size: str  # 'small', 'medium', 'enterprise'
    construction_type: str  # 'residential', 'commercial', 'infrastructure', 'industrial'
    phone_number: Optional[str] = None

class OnboardingProgress(BaseModel):
    current_step: int
    completed_steps: List[int]
    profile_completed: bool = False
    first_project_created: bool = False
    features_explored: List[str] = []

class DemoAccountRequest(BaseModel):
    account_type: str  # 'small', 'medium', 'enterprise'
    company_name: Optional[str] = None

class EmailVerification(BaseModel):
    token: str

@router.post("/register")
async def register_user(user_data: UserRegistration, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Enhanced user registration with construction-specific fields"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        company=user_data.company,
        role=user_data.role,
        company_size=user_data.company_size,
        construction_type=user_data.construction_type,
        phone_number=user_data.phone_number,
        is_active=1,
        onboarding_step=1
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Track onboarding event
    onboarding_event = OnboardingEvent(
        user_id=new_user.id,
        event_type="signup",
        event_data=json.dumps({"email": user_data.email, "company": user_data.company})
    )
    db.add(onboarding_event)
    db.commit()
    
    # Schedule welcome email
    background_tasks.add_task(send_welcome_email, new_user.id, db)
    
    return {
        "message": "Registration successful",
        "user_id": new_user.id,
        "next_step": "email_verification"
    }

@router.post("/verify-email")
async def verify_email(verification: EmailVerification, db: Session = Depends(get_db)):
    """Verify user email address"""
    
    # In a real implementation, you'd validate a verification token
    # For now, we'll just mark the email as verified
    user = db.query(User).filter(User.email == verification.token).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.email_verified = True
    user.onboarding_step = 2
    
    # Track event
    event = OnboardingEvent(
        user_id=user.id,
        event_type="email_verified",
        event_data=json.dumps({"verified_at": datetime.utcnow().isoformat()})
    )
    db.add(event)
    db.commit()
    
    return {"message": "Email verified successfully", "next_step": "profile_completion"}

@router.get("/progress")
async def get_onboarding_progress(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's onboarding progress"""
    
    completed_steps = []
    profile_completed = False
    first_project_created = False
    features_explored = []
    
    # Check completed steps
    events = db.query(OnboardingEvent).filter(OnboardingEvent.user_id == current_user.id).all()
    
    for event in events:
        if event.event_type == "signup":
            completed_steps.append(0)
        elif event.event_type == "email_verified":
            completed_steps.append(1)
        elif event.event_type == "profile_completed":
            completed_steps.append(2)
            profile_completed = True
        elif event.event_type == "first_project_created":
            completed_steps.append(3)
            first_project_created = True
        elif event.event_type == "feature_explored":
            feature_data = json.loads(event.event_data)
            features_explored.append(feature_data.get("feature_name", ""))
    
    current_step = current_user.onboarding_step
    
    return OnboardingProgress(
        current_step=current_step,
        completed_steps=completed_steps,
        profile_completed=profile_completed,
        first_project_created=first_project_created,
        features_explored=features_explored
    )

@router.post("/complete-profile")
async def complete_profile(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Mark profile as completed"""
    
    current_user.onboarding_step = 3
    
    # Track event
    event = OnboardingEvent(
        user_id=current_user.id,
        event_type="profile_completed",
        event_data=json.dumps({"completed_at": datetime.utcnow().isoformat()})
    )
    db.add(event)
    db.commit()
    
    return {"message": "Profile completed", "next_step": "create_first_project"}

@router.post("/demo-account")
async def create_demo_account(request: DemoAccountRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a demo account with sample data"""
    
    # Generate demo email
    demo_email = f"demo-{request.account_type}-{secrets.token_hex(4)}@leanaiconstruction.com"
    demo_password = "Demo123!"
    
    # Check if demo email already exists
    existing_demo = db.query(User).filter(User.email == demo_email).first()
    if existing_demo:
        return {"demo_email": demo_email, "demo_password": demo_password, "message": "Demo account already exists"}
    
    # Create demo user
    demo_user = User(
        email=demo_email,
        hashed_password=get_password_hash(demo_password),
        full_name=f"Demo {request.account_type.title()} Contractor",
        company=request.company_name or f"Demo {request.account_type.title()} Construction",
        role="manager",
        company_size=request.account_type,
        construction_type="commercial",
        is_active=1,
        onboarding_step=4,
        demo_account=True,
        trial_expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # Create demo data in background
    background_tasks.add_task(create_demo_data, demo_user.id, request.account_type, db)
    
    return {
        "demo_email": demo_email,
        "demo_password": demo_password,
        "message": "Demo account created successfully"
    }

@router.get("/demo-accounts")
async def list_demo_accounts(db: Session = Depends(get_db)):
    """List available demo account types"""
    
    return {
        "demo_accounts": [
            {
                "type": "small",
                "name": "Small Contractor",
                "description": "3-10 projects, perfect for small construction companies",
                "features": ["Basic waste tracking", "Project management", "Simple analytics"]
            },
            {
                "type": "medium", 
                "name": "Medium Builder",
                "description": "10-50 projects, ideal for growing construction businesses",
                "features": ["Advanced waste detection", "Team collaboration", "Detailed reporting"]
            },
            {
                "type": "enterprise",
                "name": "Enterprise Client", 
                "description": "50+ projects, designed for large construction corporations",
                "features": ["AI-powered predictions", "Custom integrations", "White-label options"]
            }
        ]
    }

@router.post("/track-event")
async def track_onboarding_event(
    event_type: str,
    event_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track onboarding events for analytics"""
    
    event = OnboardingEvent(
        user_id=current_user.id,
        event_type=event_type,
        event_data=json.dumps(event_data)
    )
    db.add(event)
    db.commit()
    
    # Update user's onboarding step based on event
    if event_type == "first_project_created" and current_user.onboarding_step < 4:
        current_user.onboarding_step = 4
    elif event_type == "feature_explored" and current_user.onboarding_step < 5:
        current_user.onboarding_step = 5
        current_user.is_onboarded = True
        current_user.onboarding_completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Event tracked successfully"}

def send_welcome_email(user_id: int, db: Session):
    """Send welcome email to new user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Create email template
    subject = "Welcome to Lean AI Construction - Get Started in 5 Minutes"
    
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">Welcome to Lean AI Construction!</h1>
        </div>
        
        <div style="padding: 40px 20px;">
            <h2>Hi {user.full_name},</h2>
            
            <p>Thank you for joining Lean AI Construction! We're excited to help you transform your construction projects with AI-powered insights.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057;">🚀 Quick Start Guide</h3>
                <ol>
                    <li><strong>Verify your email</strong> - Click the verification link we sent</li>
                    <li><strong>Complete your profile</strong> - Tell us about your projects</li>
                    <li><strong>Create your first project</strong> - Start tracking waste and analytics</li>
                    <li><strong>Explore AI features</strong> - Discover waste detection and predictions</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://leanaiconstruction.com/dashboard" 
                   style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    🚀 Get Started Now
                </a>
            </div>
            
            <p>Need help? Reply to this email or check out our <a href="https://leanaiconstruction.com/help">help center</a>.</p>
            
            <p>Best regards,<br>The Lean AI Construction Team</p>
        </div>
    </body>
    </html>
    """
    
    # Save email notification
    email_notification = EmailNotification(
        user_id=user.id,
        email_type="welcome",
        subject=subject,
        content=content,
        status="pending"
    )
    db.add(email_notification)
    db.commit()
    
    # In a real implementation, you would send the actual email here
    print(f"Welcome email queued for {user.email}")

def create_demo_data(user_id: int, account_type: str, db: Session):
    """Create sample data for demo accounts"""
    
    # Demo projects based on account type
    project_configs = {
        "small": [
            {"name": "Residential Home Build", "budget": 250000, "tasks": 8, "waste_logs": 3},
            {"name": "Small Office Renovation", "budget": 75000, "tasks": 12, "waste_logs": 2}
        ],
        "medium": [
            {"name": "Commercial Building Phase 1", "budget": 1200000, "tasks": 25, "waste_logs": 8},
            {"name": "Shopping Center Development", "budget": 2800000, "tasks": 45, "waste_logs": 12},
            {"name": "Industrial Warehouse", "budget": 850000, "tasks": 18, "waste_logs": 5}
        ],
        "enterprise": [
            {"name": "Hospital Complex Construction", "budget": 15000000, "tasks": 120, "waste_logs": 25},
            {"name": "Airport Terminal Expansion", "budget": 25000000, "tasks": 180, "waste_logs": 35},
            {"name": "University Campus Development", "budget": 8000000, "tasks": 85, "waste_logs": 18},
            {"name": "Skyscraper Project", "budget": 45000000, "tasks": 200, "waste_logs": 45}
        ]
    }
    
    projects = project_configs.get(account_type, project_configs["small"])
    
    for i, project_config in enumerate(projects):
        # Create project
        demo_project = Project(
            name=project_config["name"],
            description=f"Demo project for {account_type} construction company",
            owner_id=user_id,
            budget=project_config["budget"],
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow() + timedelta(days=90),
            status="active"
        )
        db.add(demo_project)
        db.commit()
        db.refresh(demo_project)
        
        # Create demo tasks
        for j in range(project_config["tasks"]):
            task = Task(
                project_id=demo_project.id,
                name=f"Task {j+1} - {project_config['name']}",
                description=f"Demo task description for {project_config['name']}",
                status="completed" if j < project_config["tasks"] * 0.7 else "pending",
                priority="high" if j < 3 else "medium",
                estimated_hours=8.0,
                actual_hours=7.5 if j < project_config["tasks"] * 0.7 else None
            )
            db.add(task)
        
        # Create demo waste logs
        for k in range(project_config["waste_logs"]):
            waste_types = ["defects", "waiting", "transportation", "overprocessing", "inventory"]
            waste_log = WasteLog(
                project_id=demo_project.id,
                waste_type=waste_types[k % len(waste_types)],
                description=f"Demo waste log {k+1} for {project_config['name']}",
                impact_cost=500.0 * (k + 1),
                impact_time=2.0 + (k * 0.5),
                detected_at=datetime.utcnow() - timedelta(days=k)
            )
            db.add(waste_log)
    
    db.commit()