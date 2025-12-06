from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
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

    projects = relationship("Project", back_populates="owner")

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
