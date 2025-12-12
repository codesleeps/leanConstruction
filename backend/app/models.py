from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    company = Column(String)
    role = Column(String)  # e.g., 'admin', 'manager', 'worker'
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)
    
    # Onboarding fields
    is_onboarded = Column(Boolean, default=False)
    onboarding_completed_at = Column(DateTime, nullable=True)
    company_size = Column(String)  # 'small' (3-10), 'medium' (10-50), 'enterprise' (50+)
    construction_type = Column(String)  # 'residential', 'commercial', 'infrastructure', 'industrial'
    phone_number = Column(String, nullable=True)
    onboarding_step = Column(Integer, default=0)  # Track onboarding progress (0-5)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    demo_account = Column(Boolean, default=False)  # Mark as demo account
    trial_expires_at = Column(DateTime, nullable=True)

    projects = relationship("Project", back_populates="owner")
    onboarding_events = relationship("OnboardingEvent", back_populates="user")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="active")  # 'active', 'completed', 'on_hold'
    budget = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    waste_logs = relationship("WasteLog", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    description = Column(Text)
    status = Column(String, default="pending")  # 'pending', 'in_progress', 'completed'
    priority = Column(String, default="medium")  # 'low', 'medium', 'high'
    assigned_to = Column(Integer, ForeignKey("users.id"))
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")

class WasteLog(Base):
    __tablename__ = "waste_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    waste_type = Column(String)  # e.g., 'defects', 'waiting', 'transportation'
    description = Column(Text)
    impact_cost = Column(Float)
    impact_time = Column(Float)  # in hours
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="waste_logs")

class OnboardingEvent(Base):
    __tablename__ = "onboarding_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String)  # 'signup', 'email_verified', 'profile_completed', 'first_project', 'feature_used'
    event_data = Column(Text)  # JSON string with event details
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="onboarding_events")

class EmailNotification(Base):
    __tablename__ = "email_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email_type = Column(String)  # 'welcome', 'onboarding_guide', 'progress_update', 'feature_announcement', 'reengagement'
    subject = Column(String)
    content = Column(Text)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'sent', 'opened', 'clicked', 'bounced'

    user = relationship("User")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lead_name = Column(String)
    lead_email = Column(String)
    lead_phone = Column(String, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="scheduled")  # 'scheduled', 'cancelled', 'completed'
    notes = Column(Text, nullable=True)
    meeting_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

class MLUsageLog(Base):
    __tablename__ = "ml_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)  # e.g., 'llama3', 'gpt-4', 'resnet-50'
    endpoint = Column(String)  # e.g., '/api/v1/ml/analyze-waste'
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    latency_ms = Column(Float)
    error_occurred = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
