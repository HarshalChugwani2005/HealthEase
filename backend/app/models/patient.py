from beanie import Document
from pydantic import Field
from typing import Optional, List, List
from datetime import datetime, date
from beanie import PydanticObjectId as ObjectId


class MedicalHistoryEntry(dict):
    """Embedded document for medical history"""
    condition: str
    diagnosed_date: datetime
    notes: Optional[str] = None


class Patient(Document):
    """Patient model"""
    user_id: ObjectId = Field(index=True)
    full_name: str
    phone: str = Field(index=True)
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    address: str = ""
    city: str = ""
    state: str = ""
    medical_history: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "patients"
        indexes = [
            "user_id",
            "phone"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone": "+919876543210",
                "date_of_birth": "1990-01-01",
                "blood_group": "O+"
            }
        }
