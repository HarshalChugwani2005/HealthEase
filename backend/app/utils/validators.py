from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
import re


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number format"""
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains digits
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True


def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode (6 digits)"""
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, pincode))
