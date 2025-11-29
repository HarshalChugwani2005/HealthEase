from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
    Token
)
from app.models.user import User, UserRole
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.wallet import Wallet
from app.utils.validators import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.middleware.auth import get_current_user
from datetime import datetime
import logging
from app.database import db
from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """
    Register a new user (patient, hospital, or admin)
    """
    if not db.connected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database unavailable. Please try again later.")
    if not db.connected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable. Please try again later.")
    # Check if user already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        is_active=True
    )
    await user.insert()
    
    # Create role-specific profile
    if request.role == UserRole.HOSPITAL:
        profile_data = request.profile_data
        hospital = Hospital(
            user_id=user.id,
            name=profile_data.get("name", ""),
            address=profile_data.get("address", ""),
            city=profile_data.get("city", ""),
            state=profile_data.get("state", ""),
            pincode=profile_data.get("pincode", ""),
            location=profile_data.get("location", {"type": "Point", "coordinates": [0, 0]}),
            phone=profile_data.get("phone", ""),
            email=request.email,
            specializations=profile_data.get("specializations", [])
        )
        await hospital.insert()
        
        # Create wallet for hospital
        wallet = Wallet(hospital_id=hospital.id)
        await wallet.insert()
        hospital.wallet_id = wallet.id
        await hospital.save()
        
        logger.info(f"Created hospital profile and wallet for user {user.id}")
    
    elif request.role == UserRole.PATIENT:
        profile_data = request.profile_data
        patient = Patient(
            user_id=user.id,
            full_name=profile_data.get("full_name", ""),
            phone=profile_data.get("phone", ""),
            date_of_birth=profile_data.get("date_of_birth"),
            blood_group=profile_data.get("blood_group"),
            address=profile_data.get("address", ""),
            city=profile_data.get("city", ""),
            state=profile_data.get("state", "")
        )
        await patient.insert()
        logger.info(f"Created patient profile for user {user.id}")
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active
        ),
        access_token=access_token
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLoginRequest):
    """
    Login user and return JWT token
    """
    if not db.connected:
        # If demo auth fallback is enabled, allow login without DB
        if settings.demo_auth_enabled:
            if request.email == settings.demo_user_email and request.password == settings.demo_user_password:
                # Return a synthetic token and minimal user info
                access_token = create_access_token(data={"sub": "demo-user-id", "role": UserRole.PATIENT.value})
                return AuthResponse(
                    user=UserResponse(
                        id="demo-user-id",
                        email=settings.demo_user_email,
                        role=UserRole.PATIENT.value,
                        is_active=True
                    ),
                    access_token=access_token
                )
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable. Please try again later.")
        # Default: service unavailable
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database unavailable. Please try again later.")
    # Find user by email
    user = await User.find_one(User.email == request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.updated_at = datetime.utcnow()
    await user.save()
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    logger.info(f"User {user.email} logged in successfully")
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active
        ),
        access_token=access_token
    )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information with profile details
    """
    if not db.connected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database unavailable. Please try again later.")
    response = {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }
    
    if current_user.role == UserRole.PATIENT:
        patient = await Patient.find_one(Patient.user_id == current_user.id)
        if patient:
            response["profile"] = {
                "full_name": patient.full_name,
                "phone": patient.phone,
                "blood_group": patient.blood_group,
                "date_of_birth": patient.date_of_birth,
                "address": patient.address,
                "city": patient.city,
                "state": patient.state
            }
            
    elif current_user.role == UserRole.HOSPITAL:
        hospital = await Hospital.find_one(Hospital.user_id == current_user.id)
        if hospital:
            response["profile"] = {
                "id": str(hospital.id),
                "name": hospital.name,
                "phone": hospital.phone,
                "address": hospital.address,
                "city": hospital.city,
                "state": hospital.state,
                "pincode": hospital.pincode,
                "specializations": hospital.specializations,
                "subscription": hospital.subscription
            }
            
    return response
