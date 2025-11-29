from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.referral import Referral, ReferralStatus
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.middleware.auth import get_patient_user, get_hospital_user
from app.services.payment_service import payment_service
from app.services.wallet_service import wallet_service
from bson import ObjectId
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/referrals", tags=["Referrals & Payments"])


class CreateReferralRequest(BaseModel):
    """Schema for creating a referral"""
    source_hospital_id: str
    destination_hospital_id: str
    patient_notes: Optional[str] = None


class PaymentVerificationRequest(BaseModel):
    """Schema for payment verification"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create")
async def create_referral(
    referral_data: CreateReferralRequest,
    current_user: User = Depends(get_patient_user)
):
    """
    Patient creates a referral from Hospital A to Hospital B
    Generates Razorpay order for ₹150
    """
    try:
        if not current_user.profile_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient profile not found for this user."
            )
        patient_id = ObjectId(current_user.profile_id)
        source_hospital_id = ObjectId(referral_data.source_hospital_id)
        destination_hospital_id = ObjectId(referral_data.destination_hospital_id)
        
        # Verify hospitals exist
        source_hospital = await Hospital.get(source_hospital_id)
        destination_hospital = await Hospital.get(destination_hospital_id)
        
        if not source_hospital or not destination_hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Check destination hospital has capacity
        if destination_hospital.capacity.get('available_beds', 0) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Destination hospital has no available beds"
            )
        
        # Create referral
        referral = Referral(
            patient_id=patient_id,
            source_hospital_id=source_hospital_id,
            destination_hospital_id=destination_hospital_id,
            status=ReferralStatus.PENDING,
            patient_notes=referral_data.patient_notes or "",
            created_at=datetime.utcnow()
        )
        await referral.insert()
        
        # Create Razorpay order
        order = payment_service.create_order(
            amount=15000,  # ₹150 in paise
            currency="INR",
            receipt=f"referral_{referral.id}",
            notes={
                "referral_id": str(referral.id),
                "patient_id": str(patient_id),
                "source_hospital": source_hospital.name,
                "destination_hospital": destination_hospital.name
            }
        )
        
        # Update referral with order ID
        referral.payment_order_id = order['id']
        await referral.save()
        
        logger.info(f"Created referral {referral.id} with Razorpay order {order['id']}")
        
        return {
            "referral_id": str(referral.id),
            "status": referral.status,
            "amount": 150,
            "razorpay_order_id": order['id'],
            "razorpay_key_id": payment_service.razorpay_key_id,
            "source_hospital": {
                "id": str(source_hospital.id),
                "name": source_hospital.name,
                "city": source_hospital.city
            },
            "destination_hospital": {
                "id": str(destination_hospital.id),
                "name": destination_hospital.name,
                "city": destination_hospital.city,
                "available_beds": destination_hospital.capacity.get('available_beds')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create referral error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/verify-payment")
async def verify_payment(
    payment_data: PaymentVerificationRequest,
    current_user: User = Depends(get_patient_user)
):
    """
    Verify Razorpay payment and distribute funds to wallets
    ₹40 → Platform
    ₹110 → Split between hospitals (AI logic)
    """
    try:
        # Verify signature
        is_valid = payment_service.verify_signature(
            razorpay_order_id=payment_data.razorpay_order_id,
            razorpay_payment_id=payment_data.razorpay_payment_id,
            razorpay_signature=payment_data.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature"
            )
        
        # Find referral by order ID
        referral = await Referral.find_one(
            Referral.payment_order_id == payment_data.razorpay_order_id
        )
        
        if not referral:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral not found"
            )
        
        # Security check: ensure the user verifying is the one who created the referral
        if referral.patient_id != ObjectId(current_user.profile_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to verify this payment."
            )

        # Update referral status
        referral.payment_id = payment_data.razorpay_payment_id
        referral.payment_status = "completed"
        referral.status = ReferralStatus.ACCEPTED
        referral.payment_completed_at = datetime.utcnow()
        await referral.save()
        
        # Get hospitals
        source_hospital = await Hospital.get(referral.source_hospital_id)
        destination_hospital = await Hospital.get(referral.destination_hospital_id)
        
        # Calculate revenue split using AI logic
        distance_factor = 0.5  # Simplified - should calculate actual distance
        capacity_factor = destination_hospital.get_occupancy_percentage() / 100
        
        # Higher split for destination (they're taking the patient)
        destination_split = 60 + (capacity_factor * 10)  # 60-70%
        source_split = 100 - destination_split  # 30-40%
        
        hospital_share = 110  # Total ₹110 for hospitals
        destination_amount = (hospital_share * destination_split) / 100
        source_amount = hospital_share - destination_amount
        
        # Credit wallets
        await wallet_service.credit_wallet(
            referral.destination_hospital_id,
            destination_amount,
            TransactionType.REFERRAL_EARNING,
            f"Referral from {source_hospital.name}",
            str(referral.id)
        )
        
        await wallet_service.credit_wallet(
            referral.source_hospital_id,
            source_amount,
            TransactionType.REFERRAL_EARNING,
            f"Referral to {destination_hospital.name}",
            str(referral.id)
        )
        
        logger.info(f"Payment verified for referral {referral.id}. " +
                   f"Destination: ₹{destination_amount:.2f}, Source: ₹{source_amount:.2f}")
        
        return {
            "message": "Payment verified and wallets credited",
            "referral_id": str(referral.id),
            "payment_id": payment_data.razorpay_payment_id,
            "amount_paid": 150,
            "distribution": {
                "platform_fee": 40,
                "destination_hospital": {
                    "name": destination_hospital.name,
                    "amount": round(destination_amount, 2)
                },
                "source_hospital": {
                    "name": source_hospital.name,
                    "amount": round(source_amount, 2)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-referrals")
async def get_my_referrals(
    current_user: User = Depends(get_patient_user)
):
    """
    Get all referrals for current patient
    """
    try:
        if not current_user.profile_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient profile not found for this user."
            )
        patient_id = ObjectId(current_user.profile_id)
        
        referrals = await Referral.find(
            Referral.patient_id == patient_id
        ).sort("-created_at").to_list()
        
        result = []
        for ref in referrals:
            source = await Hospital.get(ref.source_hospital_id)
            destination = await Hospital.get(ref.destination_hospital_id)
            
            result.append({
                "id": str(ref.id),
                "status": ref.status,
                "payment_status": ref.payment_status,
                "created_at": ref.created_at.isoformat(),
                "source_hospital": {
                    "name": source.name if source else "Unknown",
                    "city": source.city if source else ""
                },
                "destination_hospital": {
                    "name": destination.name if destination else "Unknown",
                    "city": destination.city if destination else ""
                },
                "amount_paid": 150 if ref.payment_status == "completed" else 0
            })
        
        return {
            "referrals": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Get referrals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/hospital-referrals")
async def get_hospital_referrals(
    referral_type: str = "incoming",  # incoming or outgoing
    current_user: User = Depends(get_hospital_user)
):
    """
    Get referrals for hospital (incoming or outgoing)
    Requires hospital role
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        if referral_type == "incoming":
            referrals = await Referral.find(
                Referral.destination_hospital_id == hospital_id
            ).sort("-created_at").to_list()
        else:
            referrals = await Referral.find(
                Referral.source_hospital_id == hospital_id
            ).sort("-created_at").to_list()
        
        result = []
        for ref in referrals:
            patient = await Patient.get(ref.patient_id)
            other_hospital_id = ref.source_hospital_id if referral_type == "incoming" else ref.destination_hospital_id
            other_hospital = await Hospital.get(other_hospital_id)
            
            result.append({
                "id": str(ref.id),
                "status": ref.status,
                "payment_status": ref.payment_status,
                "created_at": ref.created_at.isoformat(),
                "patient_name": patient.full_name if patient else "Unknown",
                "patient_phone": patient.phone if patient else "",
                "other_hospital": {
                    "name": other_hospital.name if other_hospital else "Unknown",
                    "city": other_hospital.city if other_hospital else ""
                },
                "notes": ref.patient_notes
            })
        
        return {
            "referral_type": referral_type,
            "hospital_id": str(hospital_id),
            "referrals": result,
            "count": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get hospital referrals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
