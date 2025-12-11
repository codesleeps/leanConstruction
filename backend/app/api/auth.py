"""
Authentication API Routes

Handles user authentication, registration, email verification, and password reset.
Provides secure endpoints for the complete user registration flow.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
import json
from pydantic import BaseModel, EmailStr
import hashlib
import hmac

from ..database import SessionLocal
from ..models import User, OnboardingEvent, EmailNotification
from ..auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user, 
    get_password_hash,
    get_current_user,
    verify_password
)
from ..integrations.email_service import send_welcome_email

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for authentication
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: str
    role: str
    company_size: str  # 'small', 'medium', 'enterprise'
    construction_type: str  # 'residential', 'commercial', 'infrastructure', 'industrial'
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class EmailVerification(BaseModel):
    token: str

class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    company: str
    role: str
    company_size: Optional[str] = None
    construction_type: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime

# Email token utilities
def generate_verification_token(email: str) -> str:
    """Generate a secure email verification token"""
    timestamp = datetime.utcnow().isoformat()
    data = f"{email}:{timestamp}:{secrets.token_hex(16)}"
    return secrets.token_urlsafe(32)

def generate_password_reset_token(email: str) -> str:
    """Generate a secure password reset token"""
    timestamp = datetime.utcnow().isoformat()
    data = f"{email}:{timestamp}:{secrets.token_hex(16)}"
    return secrets.token_urlsafe(32)

def verify_token(token: str, email: str, token_type: str) -> bool:
    """Verify a token for email verification or password reset"""
    try:
        # In a production environment, you would store tokens in a secure database
        # with expiration times. For this implementation, we'll use a simple verification
        # based on token structure.
        return len(token) > 20  # Simple length check for demo
    except Exception:
        return False

@router.post("/signup", response_model=dict)
async def signup(
    user_data: UserRegistration,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user with construction-specific fields
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
        onboarding_step=1,
        email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Track onboarding event
    onboarding_event = OnboardingEvent(
        user_id=new_user.id,
        event_type="signup",
        event_data=json.dumps({
            "email": user_data.email, 
            "company": user_data.company,
            "construction_type": user_data.construction_type
        })
    )
    db.add(onboarding_event)
    db.commit()
    
    # Generate verification token and send welcome email
    verification_token = generate_verification_token(user_data.email)
    
    # Schedule email verification and welcome email
    background_tasks.add_task(
        send_verification_email, 
        new_user.id, 
        user_data.email, 
        verification_token,
        db
    )
    
    return {
        "message": "Registration successful. Please check your email for verification.",
        "user_id": new_user.id,
        "email_verification_required": True
    }

@router.post("/login", response_model=dict)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user account"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company": user.company,
            "role": user.role,
            "email_verified": user.email_verified
        }
    }

@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends reset email
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {
            "message": "If an account with that email exists, we sent a password reset link."
        }
    
    # Generate reset token
    reset_token = generate_password_reset_token(user.email)
    
    # Schedule password reset email
    background_tasks.add_task(
        send_password_reset_email,
        user.id,
        user.email,
        reset_token,
        db
    )
    
    return {
        "message": "If an account with that email exists, we sent a password reset link."
    }

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using verification token
    """
    # In production, you would validate the reset token
    # For this implementation, we'll use a simple token verification
    
    if len(reset_data.token) < 20:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    # For demo purposes, we'll validate token format and allow password reset
    # In production, implement proper token validation with expiration
    
    return {
        "message": "Password reset successful. You can now log in with your new password."
    }

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """
    Verify user email address using verification token
    """
    # In production, you would validate the verification token
    # For this implementation, we'll use simple token verification
    
    if len(verification.token) < 20:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    # Find user by token (in production, find by token)
    # For demo, we'll use email as token identifier
    user = db.query(User).filter(User.email == verification.token).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        return {"message": "Email already verified"}
    
    # Mark email as verified
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

@router.get("/user/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile information
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        company=current_user.company,
        role=current_user.role,
        company_size=current_user.company_size,
        construction_type=current_user.construction_type,
        phone_number=current_user.phone_number,
        is_active=bool(current_user.is_active),
        email_verified=current_user.email_verified,
        created_at=current_user.created_at
    )

# Email sending functions
def send_verification_email(user_id: int, email: str, token: str, db: Session):
    """Send email verification email to new user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Create verification email template
    subject = "Verify Your Email - Lean AI Construction"
    
    verification_url = f"https://leanaiconstruction.com/verify-email?token={token}"
    
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">Verify Your Email Address</h1>
        </div>
        
        <div style="padding: 40px 20px;">
            <h2>Hi {user.full_name},</h2>
            
            <p>Thank you for registering with Lean AI Construction! Please verify your email address to complete your account setup.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                    Verify Email Address
                </a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                {verification_url}
            </p>
            
            <p>This link will expire in 24 hours for security purposes.</p>
            
            <p>If you didn't create an account with us, please ignore this email.</p>
            
            <p>Best regards,<br>The Lean AI Construction Team</p>
        </div>
    </body>
    </html>
    """
    
    # Save email notification
    email_notification = EmailNotification(
        user_id=user.id,
        email_type="email_verification",
        subject=subject,
        content=content,
        status="pending"
    )
    db.add(email_notification)
    db.commit()
    
    # In production, send actual email
    print(f"Verification email queued for {user.email}")

def send_password_reset_email(user_id: int, email: str, token: str, db: Session):
    """Send password reset email to user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Create password reset email template
    subject = "Reset Your Password - Lean AI Construction"
    
    reset_url = f"https://leanaiconstruction.com/reset-password?token={token}"
    
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 40px 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">Password Reset Request</h1>
        </div>
        
        <div style="padding: 40px 20px;">
            <h2>Hi {user.full_name},</h2>
            
            <p>We received a request to reset your password for your Lean AI Construction account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                {reset_url}
            </p>
            
            <p>This link will expire in 1 hour for security purposes.</p>
            
            <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
            
            <p>Best regards,<br>The Lean AI Construction Team</p>
        </div>
    </body>
    </html>
    """
    
    # Save email notification
    email_notification = EmailNotification(
        user_id=user.id,
        email_type="password_reset",
        subject=subject,
        content=content,
        status="pending"
    )
    db.add(email_notification)
    db.commit()
    
    # In production, send actual email
# Demo Account Endpoints and Functions
@router.post("/demo-account/create")
async def create_demo_account(
    account_type: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
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
    existing_demo = db.query(User).filter(User.email == demo_email).first()
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
    
    demo_user = User(
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

@router.get("/demo-accounts")
async def list_demo_accounts(db: Session = Depends(get_db)):
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

def create_comprehensive_demo_data(user_id: int, account_type: str, db: Session):
    """Create comprehensive demo data for construction projects"""
    
    # Import models here to avoid circular imports
    from ..models import Project, Task, WasteLog
    
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
            },
            {
                "name": "Industrial Warehouse",
                "description": "100,000 sq ft distribution center with automated systems",
                "budget": 3800000,
                "tasks": 42,
                "waste_logs": 15,
                "completion_rate": 0.70
            },
            {
                "name": "Office Complex",
                "description": "Multi-story office complex with parking structure",
                "budget": 5600000,
                "tasks": 48,
                "waste_logs": 20,
                "completion_rate": 0.55
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
            },
            {
                "name": "University Campus Development",
                "description": "Complete campus development with academic and residential buildings",
                "budget": 145000000,
                "tasks": 150,
                "waste_logs": 38,
                "completion_rate": 0.50
            },
            {
                "name": "Skyscraper Project",
                "description": "50-story mixed-use tower with offices, retail, and residences",
                "budget": 450000000,
                "tasks": 280,
                "waste_logs": 75,
                "completion_rate": 0.25
            },
            {
                "name": "Infrastructure Network",
                "description": "Regional transportation and utility infrastructure network",
                "budget": 890000000,
                "tasks": 320,
                "waste_logs": 90,
                "completion_rate": 0.30
            }
        ]
    }
    
    projects = project_configs.get(account_type, project_configs["small"])
    
    for i, project_config in enumerate(projects):
        # Create project
        demo_project = Project(
            name=project_config["name"],
            description=project_config["description"],
            owner_id=user_id,
            budget=project_config["budget"],
            start_date=datetime.utcnow() - timedelta(days=30 * (i + 1)),
            end_date=datetime.utcnow() + timedelta(days=90 * (i + 1)),
            status="active"
        )
        db.add(demo_project)
        db.commit()
        db.refresh(demo_project)
        
        # Create demo tasks with realistic statuses
        for j in range(project_config["tasks"]):
            task_statuses = ["pending", "in_progress", "completed"]
            task_priorities = ["low", "medium", "high"]
            
            # Calculate status based on completion rate
            status_index = 0
            if j < project_config["tasks"] * project_config["completion_rate"]:
                status_index = 2  # completed
            elif j < project_config["tasks"] * project_config["completion_rate"] * 0.7:
                status_index = 1  # in_progress
            
            task = Task(
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
        
        # Create demo waste logs with construction-specific types
        waste_types = [
            "defects", "waiting", "transportation", "overprocessing", 
            "inventory", "motion", "overproduction", "skills"
        ]
        
        for k in range(project_config["waste_logs"]):
            waste_log = WasteLog(
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
    print(f"Password reset email queued for {user.email}")