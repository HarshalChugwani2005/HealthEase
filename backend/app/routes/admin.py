from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import User
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.referral import Referral
from app.models.wallet import Wallet, WalletTransaction
from app.models.advertisement import Advertisement
from app.models.workflow_log import WorkflowLog
from app.middleware.auth import get_admin_user
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/hospitals")
async def list_all_hospitals(
    subscription_plan: Optional[str] = None,
    current_user: User = Depends(get_admin_user)
):
    """
    List all hospitals with subscription status (admin only)
    """
    query = {}
    if subscription_plan:
        query["subscription.plan"] = subscription_plan
    
    hospitals = await Hospital.find(query).to_list()
    
    result = []
    for hospital in hospitals:
        # Get wallet balance
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital.id)
        
        result.append({
            "id": str(hospital.id),
            "name": hospital.name,
            "city": hospital.city,
            "email": hospital.email,
            "phone": hospital.phone,
            "subscription": hospital.subscription,
            "wallet_balance": wallet.balance if wallet else 0,
            "capacity": hospital.capacity,
            "occupancy": hospital.get_occupancy_percentage(),
            "created_at": hospital.created_at
        })
    
    return {"hospitals": result, "count": len(result)}


@router.put("/hospitals/{hospital_id}/subscription")
async def update_hospital_subscription(
    hospital_id: str,
    subscription_data: dict,
    current_user: User = Depends(get_admin_user)
):
    """
    Update hospital subscription plan
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        hospital.subscription.update(subscription_data)
        hospital.updated_at = datetime.utcnow()
        await hospital.save()
        
        logger.info(f"Admin updated subscription for hospital {hospital_id}")
        
        return {
            "message": "Subscription updated",
            "subscription": hospital.subscription
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics")
async def get_system_analytics(current_user: User = Depends(get_admin_user)):
    """
    Get system-wide analytics
    """
    # Count hospitals by subscription
    total_hospitals = await Hospital.find_all().count()
    free_hospitals = await Hospital.find({"subscription.plan": "free"}).count()
    paid_hospitals = await Hospital.find({"subscription.plan": "paid"}).count()
    
    # Count patients
    total_patients = await Patient.find_all().count()
    
    # Count referrals by status
    total_referrals = await Referral.find_all().count()
    completed_referrals = await Referral.find({"status": "completed"}).count()
    pending_referrals = await Referral.find({"status": "pending"}).count()
    
    # Calculate revenue (platform fees from completed referrals)
    completed_refs = await Referral.find({"status": "completed"}).to_list()
    total_revenue = sum(r.payment.get("platform_fee", 40) for r in completed_refs)
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_referrals = await Referral.find(
        Referral.created_at >= thirty_days_ago
    ).count()
    
    # Hospital distribution by city
    all_hospitals = await Hospital.find_all().to_list()
    city_distribution = {}
    for hospital in all_hospitals:
        city = hospital.city
        if city in city_distribution:
            city_distribution[city] += 1
        else:
            city_distribution[city] = 1
    
    return {
        "hospitals": {
            "total": total_hospitals,
            "free": free_hospitals,
            "paid": paid_hospitals
        },
        "patients": {
            "total": total_patients
        },
        "referrals": {
            "total": total_referrals,
            "completed": completed_referrals,
            "pending": pending_referrals,
            "last_30_days": recent_referrals
        },
        "revenue": {
            "total_platform_fees": total_revenue,
            "currency": "INR"
        },
        "geographic_distribution": city_distribution
    }


@router.post("/advertisements")
async def create_advertisement(
    ad_data: dict,
    current_user: User = Depends(get_admin_user)
):
    """
    Create advertisement for a hospital
    """
    try:
        hospital_id = ObjectId(ad_data["hospital_id"])
        hospital = await Hospital.get(hospital_id)
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        ad = Advertisement(
            hospital_id=hospital_id,
            title=ad_data["title"],
            description=ad_data["description"],
            image_url=ad_data.get("image_url"),
            link_url=ad_data.get("link_url"),
            is_active=ad_data.get("is_active", True)
        )
        await ad.insert()
        
        logger.info(f"Admin created advertisement for hospital {hospital_id}")
        
        return {
            "message": "Advertisement created",
            "ad_id": str(ad.id)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/advertisements")
async def list_advertisements(current_user: User = Depends(get_admin_user)):
    """
    List all advertisements
    """
    ads = await Advertisement.find_all().to_list()
    
    result = []
    for ad in ads:
        hospital = await Hospital.get(ad.hospital_id)
        
        result.append({
            "id": str(ad.id),
            "hospital_name": hospital.name if hospital else "Unknown",
            "hospital_id": str(ad.hospital_id),
            "title": ad.title,
            "description": ad.description,
            "is_active": ad.is_active,
            "metrics": ad.metrics,
            "ctr": ad.get_ctr(),
            "created_at": ad.created_at
        })
    
    return {"advertisements": result}


@router.put("/advertisements/{ad_id}")
async def update_advertisement(
    ad_id: str,
    ad_data: dict,
    current_user: User = Depends(get_admin_user)
):
    """
    Update advertisement
    """
    try:
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(status_code=404, detail="Advertisement not found")
        
        for key, value in ad_data.items():
            if hasattr(ad, key) and key not in ["id", "hospital_id", "created_at", "metrics"]:
                setattr(ad, key, value)
        
        ad.updated_at = datetime.utcnow()
        await ad.save()
        
        return {"message": "Advertisement updated"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet-transactions")
async def get_all_wallet_transactions(
    limit: int = 100,
    current_user: User = Depends(get_admin_user)
):
    """
    Get all wallet transactions across the platform
    """
    transactions = await WalletTransaction.find_all().sort(
        -WalletTransaction.created_at
    ).limit(limit).to_list()
    
    result = []
    for t in transactions:
        wallet = await Wallet.get(t.wallet_id)
        hospital = await Hospital.find_one(Wallet.hospital_id == wallet.hospital_id) if wallet else None
        
        result.append({
            "id": str(t.id),
            "hospital_name": hospital.name if hospital else "Unknown",
            "type": t.transaction_type,
            "amount": t.amount,
            "description": t.description,
            "created_at": t.created_at
        })
    
    return {"transactions": result, "count": len(result)}


@router.post("/payouts/{hospital_id}")
async def process_payout(
    hospital_id: str,
    payout_data: dict,
    current_user: User = Depends(get_admin_user)
):
    """
    Process payout for hospital (admin approval required)
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital.id)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        amount = payout_data["amount"]
        
        if amount > wallet.balance:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Deduct from wallet
        await wallet.debit(amount)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type="withdrawal",
            amount=amount,
            description=f"Payout approved by admin - {payout_data.get('notes', '')}"
        )
        await transaction.insert()
        
        logger.info(f"Admin processed payout of ₹{amount} for hospital {hospital_id}")
        
        return {
            "message": "Payout processed",
            "amount": amount,
            "remaining_balance": wallet.balance
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/n8n-logs")
async def get_n8n_logs(
    workflow_name: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_admin_user)
):
    """
    View n8n workflow execution logs
    """
    query = {}
    if workflow_name:
        query = {"workflow_name": workflow_name}
    
    logs = await WorkflowLog.find(query).sort(
        -WorkflowLog.created_at
    ).limit(limit).to_list()
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "workflow_name": log.workflow_name,
                "execution_id": log.execution_id,
                "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }
