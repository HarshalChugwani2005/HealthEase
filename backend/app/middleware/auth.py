from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_access_token
from app.models.user import User, UserRole
from typing import Optional, List
from bson import ObjectId


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Demo auth fallback: return synthetic user object for demo-user-id
    if user_id == "demo-user-id":
        # Create a mock User object with demo credentials
        from app.config import settings
        demo_user = User(
            email=settings.demo_user_email,
            password_hash="",  # Not used for demo
            role=UserRole.PATIENT,
            is_active=True
        )
        demo_user.id = user_id  # Set the ID directly
        return demo_user
    
    # Fetch user from database
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency to check if user has required role
    
    Args:
        allowed_roles: List of allowed user roles
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for specific roles
async def get_patient_user(current_user: User = Depends(require_role([UserRole.PATIENT]))) -> User:
    """Dependency to get current patient user"""
    return current_user


async def get_hospital_user(current_user: User = Depends(require_role([UserRole.HOSPITAL]))) -> User:
    """Dependency to get current hospital user"""
    return current_user


async def get_admin_user(current_user: User = Depends(require_role([UserRole.ADMIN]))) -> User:
    """Dependency to get current admin user"""
    return current_user
