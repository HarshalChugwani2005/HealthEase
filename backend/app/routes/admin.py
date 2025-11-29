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
    Enhanced system-wide analytics dashboard
    """
    # Count hospitals by subscription
    total_hospitals = await Hospital.find_all().count()
    free_hospitals = await Hospital.find(Hospital.subscription_tier == "free").count()
    paid_hospitals = await Hospital.find(Hospital.subscription_tier == "paid").count()
    verified_hospitals = await Hospital.find(Hospital.is_verified == True).count()
    
    # Count patients
    total_patients = await Patient.find_all().count()
    
    # Count referrals by status
    all_referrals = await Referral.find_all().to_list()
    total_referrals = len(all_referrals)
    completed_referrals = sum(1 for r in all_referrals if r.payment_status == "completed")
    pending_referrals = sum(1 for r in all_referrals if r.payment_status == "pending")
    
    # Calculate revenue (platform fees from completed referrals)
    total_revenue = completed_referrals * 40  # ₹40 platform fee per referral
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_referrals = sum(1 for r in all_referrals if r.created_at >= thirty_days_ago)
    
    # Get all wallets for total ecosystem value
    all_wallets = await Wallet.find_all().to_list()
    total_wallet_balance = sum(w.balance for w in all_wallets)
    total_earned = sum(w.total_earned for w in all_wallets)
    total_withdrawn = sum(w.total_withdrawn for w in all_wallets)
    
    # Get pending payouts
    from app.models.wallet import PayoutRequest, PayoutStatus
    pending_payouts = await PayoutRequest.find(
        PayoutRequest.status == PayoutStatus.PENDING
    ).to_list()
    pending_payout_amount = sum(p.amount for p in pending_payouts)
    
    # Hospital distribution by city
    all_hospitals = await Hospital.find_all().to_list()
    city_distribution = {}
    state_distribution = {}
    for hospital in all_hospitals:
        city = hospital.city
        state = hospital.state
        if city in city_distribution:
            city_distribution[city] += 1
        else:
            city_distribution[city] = 1
        if state in state_distribution:
            state_distribution[state] += 1
        else:
            state_distribution[state] = 1
    
    # Top cities by hospital count
    top_cities = sorted(city_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate system health metrics
    avg_occupancy = sum(h.get_occupancy_percentage() for h in all_hospitals) / len(all_hospitals) if all_hospitals else 0
    
    return {
        "overview": {
            "total_hospitals": total_hospitals,
            "verified_hospitals": verified_hospitals,
            "total_patients": total_patients,
            "total_referrals": total_referrals
        },
        "hospitals": {
            "total": total_hospitals,
            "free_tier": free_hospitals,
            "paid_tier": paid_hospitals,
            "verified": verified_hospitals,
            "average_occupancy": round(avg_occupancy, 2)
        },
        "patients": {
            "total": total_patients,
            "active": total_patients  # Placeholder - add last_login tracking
        },
        "referrals": {
            "total": total_referrals,
            "completed": completed_referrals,
            "pending": pending_referrals,
            "last_30_days": recent_referrals,
            "completion_rate": round((completed_referrals / total_referrals * 100), 2) if total_referrals > 0 else 0
        },
        "revenue": {
            "total_platform_fees": total_revenue,
            "currency": "INR",
            "average_per_referral": 40
        },
        "wallets": {
            "total_balance": round(total_wallet_balance, 2),
            "total_earned": round(total_earned, 2),
            "total_withdrawn": round(total_withdrawn, 2),
            "pending_payouts": len(pending_payouts),
            "pending_payout_amount": round(pending_payout_amount, 2)
        },
        "geographic_distribution": {
            "by_city": dict(top_cities),
            "by_state": state_distribution,
            "total_cities": len(city_distribution),
            "total_states": len(state_distribution)
        }
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


@router.get("/payouts/pending")
async def get_pending_payouts(current_user: User = Depends(get_admin_user)):
    """
    Get all pending payout requests
    """
    try:
        from app.models.wallet import PayoutRequest, PayoutStatus
        
        pending_payouts = await PayoutRequest.find(
            PayoutRequest.status == PayoutStatus.PENDING
        ).sort("-requested_at").to_list()
        
        result = []
        for payout in pending_payouts:
            hospital = await Hospital.get(payout.hospital_id)
            wallet = await Wallet.find_one(Wallet.hospital_id == payout.hospital_id)
            
            result.append({
                "id": str(payout.id),
                "hospital_id": str(payout.hospital_id),
                "hospital_name": hospital.name if hospital else "Unknown",
                "amount": payout.amount,
                "wallet_balance": wallet.balance if wallet else 0,
                "account_holder": payout.account_holder_name,
                "account_number": payout.account_number,
                "ifsc_code": payout.ifsc_code,
                "bank_name": payout.bank_name,
                "requested_at": payout.requested_at.isoformat(),
                "status": payout.status
            })
        
        return {
            "pending_payouts": result,
            "count": len(result),
            "total_amount": sum(p["amount"] for p in result)
        }
        
    except Exception as e:
        logger.error(f"Get pending payouts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/payouts/{payout_id}/approve")
async def approve_payout(
    payout_id: str,
    admin_notes: str = "",
    current_user: User = Depends(get_admin_user)
):
    """
    Approve payout request and process payment
    """
    try:
        from app.models.wallet import PayoutRequest, PayoutStatus, TransactionType
        
        payout = await PayoutRequest.get(ObjectId(payout_id))
        
        if not payout:
            raise HTTPException(status_code=404, detail="Payout request not found")
        
        if payout.status != PayoutStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Payout already {payout.status}")
        
        wallet = await Wallet.find_one(Wallet.hospital_id == payout.hospital_id)
        
        if not wallet or wallet.balance < payout.amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Deduct from wallet
        await wallet.debit(payout.amount)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=payout.amount,
            description=f"Payout approved - {payout.bank_name} ****{payout.account_number[-4:]}"
        )
        await transaction.insert()
        
        # Update payout status
        payout.status = PayoutStatus.APPROVED
        payout.processed_at = datetime.utcnow()
        payout.admin_notes = admin_notes
        await payout.save()
        
        hospital = await Hospital.get(payout.hospital_id)
        
        logger.info(f"Admin approved payout {payout_id} of ₹{payout.amount}")
        
        return {
            "message": "Payout approved and processed",
            "payout_id": str(payout.id),
            "hospital_name": hospital.name if hospital else "Unknown",
            "amount": payout.amount,
            "remaining_wallet_balance": wallet.balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve payout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/payouts/{payout_id}/reject")
async def reject_payout(
    payout_id: str,
    admin_notes: str,
    current_user: User = Depends(get_admin_user)
):
    """
    Reject payout request
    """
    try:
        from app.models.wallet import PayoutRequest, PayoutStatus
        
        payout = await PayoutRequest.get(ObjectId(payout_id))
        
        if not payout:
            raise HTTPException(status_code=404, detail="Payout request not found")
        
        if payout.status != PayoutStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Payout already {payout.status}")
        
        # Update payout status
        payout.status = PayoutStatus.REJECTED
        payout.processed_at = datetime.utcnow()
        payout.admin_notes = admin_notes
        await payout.save()
        
        hospital = await Hospital.get(payout.hospital_id)
        
        logger.info(f"Admin rejected payout {payout_id}")
        
        return {
            "message": "Payout rejected",
            "payout_id": str(payout.id),
            "hospital_name": hospital.name if hospital else "Unknown",
            "reason": admin_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reject payout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
