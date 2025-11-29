from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    PATIENT = "patient"
    HOSPITAL = "hospital"
    ADMIN = "admin"


class User(Document):
    """User model for authentication"""
    email: EmailStr = Field(unique=True, index=True)
    password_hash: str
    role: UserRole
    is_active: bool = True
    
    # Profile references
    profile_id: Optional[str] = None  # Links to Patient/Hospital ID
    hospital_id: Optional[str] = None  # For hospital users
    name: Optional[str] = None
    phone: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "role",
            "profile_id",
            "hospital_id"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "patient",
                "is_active": True
            }
        }
