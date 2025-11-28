from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole
from typing import Optional
from app.utils.validators import validate_password_strength


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    profile_data: dict = {}
    
    @validator('password')
    def password_strength(cls, v):
        if not validate_password_strength(v):
            raise ValueError(
                'Password must be at least 8 characters and contain uppercase, lowercase, and digits'
            )
        return v


class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload schema"""
    sub: str
    role: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
