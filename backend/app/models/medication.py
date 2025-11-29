from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime, time
from enum import Enum

class MedicationFrequency(str, Enum):
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily" 
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    EVERY_N_HOURS = "every_n_hours"
    AS_NEEDED = "as_needed"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class MedicationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

class DosageSchedule(BaseModel):
    time: time
    dose_amount: str
    instructions: Optional[str] = None

class MedicationInteraction(BaseModel):
    medication_name: str
    severity: str  # "mild", "moderate", "severe"
    description: str
    action_required: str

class SideEffect(BaseModel):
    name: str
    severity: str
    reported_date: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False

class MedicationAdherence(BaseModel):
    date: datetime
    scheduled_doses: int
    taken_doses: int
    missed_doses: int
    adherence_percentage: float

class Medication(Document):
    patient_id: str = Field(..., index=True)
    hospital_id: str = Field(..., index=True)
    prescribed_by: str  # Doctor ID
    
    # Medication Details
    name: str
    generic_name: Optional[str] = None
    dosage: str  # "500mg", "10ml", etc.
    form: str  # "tablet", "capsule", "syrup", etc.
    
    # Prescription Details
    frequency: MedicationFrequency
    schedule: List[DosageSchedule] = []
    duration_days: Optional[int] = None
    total_quantity: Optional[str] = None
    refills_remaining: int = 0
    
    # Instructions
    instructions: str
    food_instructions: Optional[str] = None  # "with food", "empty stomach"
    special_instructions: Optional[str] = None
    
    # Status & Tracking
    status: MedicationStatus = MedicationStatus.ACTIVE
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    
    # Interactions & Side Effects
    interactions: List[MedicationInteraction] = []
    side_effects: List[SideEffect] = []
    
    # Adherence Tracking
    adherence_logs: List[MedicationAdherence] = []
    last_taken: Optional[datetime] = None
    next_due: Optional[datetime] = None
    
    # Pharmacy Details
    pharmacy_name: Optional[str] = None
    pharmacy_contact: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "medications"
        indexes = [
            "patient_id",
            "hospital_id", 
            "prescribed_by",
            "status",
            "next_due",
            [("patient_id", 1), ("status", 1)]
        ]

class MedicationReminder(Document):
    patient_id: str = Field(..., index=True)
    medication_id: str = Field(..., index=True)
    
    # Reminder Details
    scheduled_time: datetime = Field(..., index=True)
    medication_name: str
    dosage: str
    instructions: str
    
    # Status
    sent: bool = False
    acknowledged: bool = False
    taken: bool = False
    missed: bool = False
    
    # Timestamps
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    taken_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "medication_reminders"
        indexes = [
            "patient_id",
            "medication_id",
            "scheduled_time",
            [("patient_id", 1), ("sent", 1)],
            [("scheduled_time", 1), ("sent", 1)]
        ]

class Prescription(Document):
    patient_id: str = Field(..., index=True)
    hospital_id: str = Field(..., index=True)
    doctor_id: str = Field(..., index=True)
    
    # Prescription Details
    prescription_number: str = Field(..., unique=True, index=True)
    medications: List[str] = []  # Medication IDs
    
    # Medical Context
    diagnosis: Optional[str] = None
    symptoms: List[str] = []
    notes: Optional[str] = None
    
    # Prescription Status
    status: str = "active"  # active, completed, cancelled
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    
    # Digital Signature
    digital_signature: Optional[str] = None
    verification_code: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "prescriptions"
        indexes = [
            "patient_id",
            "hospital_id",
            "doctor_id",
            "prescription_number",
            "status",
            [("patient_id", 1), ("status", 1)]
        ]