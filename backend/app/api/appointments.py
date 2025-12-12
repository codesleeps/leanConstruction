from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from ..database import SessionLocal
from ..models import Appointment, User
from ..auth import get_current_active_user
from ..integrations.email_service import send_appointment_confirmation

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AppointmentCreate(BaseModel):
    lead_name: str
    lead_email: EmailStr
    lead_phone: Optional[str] = None
    start_time: datetime
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    lead_name: str
    lead_email: str
    start_time: datetime
    end_time: datetime
    status: str
    meeting_link: Optional[str] = None

    class Config:
        orm_mode = True

@router.post("/book", response_model=AppointmentResponse)
def book_appointment(
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Book a strategy session or demo call.
    Automatically sets 45 minute duration.
    """
    # Calculate end time (default 45 mins)
    duration_minutes = 45
    end_time = appointment_data.start_time + timedelta(minutes=duration_minutes)
    
    # Check availability (simple overlap check)
    overlapping = db.query(Appointment).filter(
        Appointment.status != "cancelled",
        Appointment.start_time < end_time,
        Appointment.end_time > appointment_data.start_time
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    # Create appointment
    new_appt = Appointment(
        lead_name=appointment_data.lead_name,
        lead_email=appointment_data.lead_email,
        lead_phone=appointment_data.lead_phone,
        start_time=appointment_data.start_time,
        end_time=end_time,
        notes=appointment_data.notes,
        status="scheduled",
        meeting_link="https://meet.google.com/abc-defg-hij" # Mock link for now
    )
    
    # Associate with user if email matches existing user
    existing_user = db.query(User).filter(User.email == appointment_data.lead_email).first()
    if existing_user:
        new_appt.user_id = existing_user.id

    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)

    # Send confirmation email
    background_tasks.add_task(
        send_appointment_confirmation,
        new_appt.id,
        new_appt.lead_email,
        db
    )

    return new_appt

@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List appointments. 
    Admins see all. Regular users see their own (matched by email or user_id).
    """
    if current_user.role == "admin":
        return db.query(Appointment).offset(skip).limit(limit).all()
    else:
        return db.query(Appointment).filter(
            (Appointment.user_id == current_user.id) | 
            (Appointment.lead_email == current_user.email)
        ).all()
