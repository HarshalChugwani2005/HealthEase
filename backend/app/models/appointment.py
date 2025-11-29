from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    IN_PERSON = "in_person"
    TELEMEDICINE = "telemedicine"
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"

class Appointment(Document):
    patient_id: ObjectId = Field(index=True)
    hospital_id: ObjectId = Field(index=True)
    doctor_name: Optional[str] = None
    specialization: str
    appointment_type: AppointmentType = AppointmentType.IN_PERSON
    scheduled_time: datetime = Field(index=True)
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    patient_notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    meeting_url: Optional[str] = None  # For telemedicine
    meeting_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "appointments"
        indexes = [
            [("patient_id", 1), ("scheduled_time", 1)],
            [("hospital_id", 1), ("scheduled_time", 1)],
            [("scheduled_time", 1), ("status", 1)]
        ]