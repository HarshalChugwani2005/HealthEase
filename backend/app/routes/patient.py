from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.models.user import User
from app.models.patient import Patient
from app.models.hospital import Hospital
from app.models.referral import Referral, ReferralStatus
from app.middleware.auth import get_patient_user
from app.services.payment_service import payment_service
from app.services.wallet_service import WalletService
from app.services.ai_service import ai_service
from app.config import settings
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/me")
async def get_patient_profile(current_user: User = Depends(get_patient_user)):
    """
    Get current patient profile
    """
    patient = await Patient.find_one(Patient.user_id == current_user.id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    return {
        "id": str(patient.id),
        "full_name": patient.full_name,
        "phone": patient.phone,
        "date_of_birth": patient.date_of_birth,
        "blood_group": patient.blood_group,
        "address": patient.address,
        "city": patient.city,
        "state": patient.state,
        "medical_history": patient.medical_history
    }


@router.put("/me")
async def update_patient_profile(
    profile_data: dict,
    current_user: User = Depends(get_patient_user)
):
    """
    Update patient profile
    """
    patient = await Patient.find_one(Patient.user_id == current_user.id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Update allowed fields
    for key, value in profile_data.items():
        if hasattr(patient, key) and key not in ["id", "user_id", "created_at"]:
            setattr(patient, key, value)
    
    patient.updated_at = datetime.utcnow()
    await patient.save()
    
    return {"message": "Profile updated successfully"}


@router.get("/hospitals/search")
async def search_hospitals(
    latitude: float = Query(...),
    longitude: float = Query(...),
    specialization: Optional[str] = None,
    current_user: User = Depends(get_patient_user)
):
    """
    Search hospitals by load probability and location
    """
    # Find nearby hospitals
    radius_meters = 50000  # 50km default
    
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius_meters
            }
        }
    }
    
    if specialization:
        query["specializations"] = specialization
    
    hospitals = await Hospital.find(query).to_list()
    
    # Calculate load probability and sort
    result = []
    for hospital in hospitals:
        occupancy = hospital.get_occupancy_percentage()
        avg_occupancy = (occupancy["beds"] + occupancy["icu"] + occupancy["ventilators"]) / 3
        
        # Estimate wait time based on occupancy
        if avg_occupancy < 50:
            wait_time = "< 15 minutes"
        elif avg_occupancy < 75:
            wait_time = "15-30 minutes"
        elif avg_occupancy < 90:
            wait_time = "30-60 minutes"
        else:
            wait_time = "> 60 minutes"
        
        result.append({
            "id": str(hospital.id),
            "name": hospital.name,
            "address": hospital.address,
            "city": hospital.city,
            "phone": hospital.phone,
            "specializations": hospital.specializations,
            "location": hospital.location,
            "capacity": hospital.capacity,
            "occupancy": occupancy,
            "load_probability": hospital.get_load_probability(),
            "estimated_wait_time": wait_time,
            "has_available_beds": hospital.capacity["available_beds"] > 0
        })
    
    # Sort by load probability (low to high)
    priority_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    result.sort(key=lambda x: priority_order.get(x["load_probability"], 4))
    
    return {"hospitals": result, "count": len(result)}


@router.post("/referrals")
async def create_referral(
    referral_data: dict,
    current_user: User = Depends(get_patient_user)
):
    """
    Create a referral request from one hospital to another
    """
    try:
        patient = await Patient.find_one(Patient.user_id == current_user.id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        from_hospital_id = ObjectId(referral_data["from_hospital_id"])
        to_hospital_id = ObjectId(referral_data["to_hospital_id"])
        
        # Verify hospitals exist
        from_hospital = await Hospital.get(from_hospital_id)
        to_hospital = await Hospital.get(to_hospital_id)
        
        if not from_hospital or not to_hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Calculate AI-powered split
        split = await ai_service.calculate_referral_split(from_hospital, to_hospital)
        
        # Create referral
        referral = Referral(
            patient_id=patient.id,
            from_hospital_id=from_hospital_id,
            to_hospital_id=to_hospital_id,
            status=ReferralStatus.PENDING,
            reason=referral_data.get("reason", "Patient referred due to capacity/specialization"),
            payment={
                "patient_amount": settings.patient_referral_fee,
                "platform_fee": settings.platform_fee,
                "hospital_share": settings.hospital_share,
                "from_hospital_share": split["from_hospital_share"],
                "to_hospital_share": split["to_hospital_share"]
            }
        )
        await referral.insert()
        
        # Create Razorpay order
        amount_paise = int(settings.patient_referral_fee * 100)  # Convert to paise
        order = await payment_service.create_order(
            amount=amount_paise,
            patient_id=str(patient.id),
            referral_id=str(referral.id)
        )
        
        referral.razorpay_order_id = order["id"]
        await referral.save()
        
        logger.info(f"Created referral {referral.id} with order {order['id']}")
        
        return {
            "referral_id": str(referral.id),
            "razorpay_order": {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"]
            },
            "payment_breakdown": referral.payment
        }
    
    except Exception as e:
        logger.error(f"Failed to create referral: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/referrals/{referral_id}/payment")
async def confirm_payment(
    referral_id: str,
    payment_data: dict,
    current_user: User = Depends(get_patient_user)
):
    """
    Confirm payment and complete referral
    """
    try:
        referral = await Referral.get(ObjectId(referral_id))
        
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        # Verify patient ownership
        patient = await Patient.find_one(Patient.user_id == current_user.id)
        if str(referral.patient_id) != str(patient.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Verify payment signature
        is_valid = payment_service.verify_payment_signature(
            order_id=referral.razorpay_order_id,
            payment_id=payment_data["razorpay_payment_id"],
            signature=payment_data["razorpay_signature"]
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Update referral
        referral.razorpay_payment_id = payment_data["razorpay_payment_id"]
        referral.status = ReferralStatus.COMPLETED
        referral.updated_at = datetime.utcnow()
        await referral.save()
        
        # Process wallet credits
        await WalletService.process_referral_payment(
            referral=referral,
            from_hospital_share=referral.payment["from_hospital_share"],
            to_hospital_share=referral.payment["to_hospital_share"]
        )
        
        logger.info(f"Payment confirmed for referral {referral_id}")
        
        return {
            "message": "Payment confirmed and wallets credited",
            "referral_status": referral.status
        }
    
    except Exception as e:
        logger.error(f"Payment confirmation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/alerts")
async def get_health_alerts(current_user: User = Depends(get_patient_user)):
    """
    Get personalized health alerts based on pollution, epidemics, festivals
    """
    patient = await Patient.find_one(Patient.user_id == current_user.id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Mock alerts (in production, fetch from external APIs)
    alerts = [
        {
            "id": "alert_1",
            "type": "pollution",
            "severity": "high",
            "title": "High Air Pollution Alert",
            "message": f"AQI in {patient.city} is above 300. Avoid outdoor activities.",
            "created_at": datetime.utcnow()
        },
        {
            "id": "alert_2",
            "type": "festival",
            "severity": "medium",
            "title": "Festival Season Preparation",
            "message": "Diwali approaching. Hospitals may experience high load. Book appointments early.",
            "created_at": datetime.utcnow()
        }
    ]
    
    return {"alerts": alerts}


@router.get("/referrals")
async def get_patient_referrals(current_user: User = Depends(get_patient_user)):
    """
    Get patient's referral history
    """
    patient = await Patient.find_one(Patient.user_id == current_user.id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    referrals = await Referral.find(
        Referral.patient_id == patient.id
    ).sort(-Referral.created_at).to_list()
    
    result = []
    for r in referrals:
        from_hospital = await Hospital.get(r.from_hospital_id)
        to_hospital = await Hospital.get(r.to_hospital_id)
        
        result.append({
            "id": str(r.id),
            "from_hospital": from_hospital.name if from_hospital else "Unknown",
            "to_hospital": to_hospital.name if to_hospital else "Unknown",
            "status": r.status,
            "reason": r.reason,
            "payment_amount": r.payment["patient_amount"],
            "created_at": r.created_at
        })
    
    return {"referrals": result}
