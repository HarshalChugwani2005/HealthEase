from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import User, UserRole
from app.models.hospital import Hospital
from app.models.inventory import Inventory
from app.models.referral import Referral, ReferralStatus
from app.models.surge_prediction import SurgePrediction
from app.models.wallet import Wallet, WalletTransaction
from app.middleware.auth import get_hospital_user, get_current_user
from app.services.ai_service import ai_service
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


@router.post("/execute-action")
async def execute_agentic_action(
    action_data: dict,
    current_user: User = Depends(get_hospital_user)
):
    """
    Execute an autonomous agentic action
    """
    try:
        hospital = await Hospital.find_one(Hospital.user_id == current_user.id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital profile not found")

        action_type = action_data.get("type")
        details = action_data.get("details", {})
        
        logger.info(f"Executing agentic action: {action_type} for hospital {hospital.id}")
        
        if "capacity" in action_type.lower() or "bed" in action_type.lower():
            # Simulate capacity update
            # In a real agent, this would parse the natural language instruction
            # For now, we'll just increment available beds if the action implies increasing capacity
            if "increase" in action_type.lower() or "add" in action_type.lower():
                hospital.capacity["available_beds"] += 5
                hospital.capacity["total_beds"] += 5
                await hospital.save()
                return {"status": "success", "message": "Capacity increased by 5 beds", "new_capacity": hospital.capacity}
                
        elif "inventory" in action_type.lower() or "order" in action_type.lower():
            # Simulate inventory order
            return {"status": "success", "message": "Inventory order placed successfully", "order_id": f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M')}"}
            
        elif "staff" in action_type.lower():
            # Simulate staffing alert
            return {"status": "success", "message": "Staffing alert sent to HR department"}
            
        return {"status": "success", "message": f"Action '{action_type}' executed successfully"}
        
    except Exception as e:
        logger.error(f"Agentic action error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_hospitals(
    city: Optional[str] = None,
    specialization: Optional[str] = None,
    has_beds: Optional[bool] = None
):
    """
    List all hospitals with optional filters
    """
    query = {}
    
    if city:
        query["city"] = city
    
    if specialization:
        query["specializations"] = specialization
    
    if has_beds:
        query["capacity.available_beds"] = {"$gt": 0}
    
    hospitals = await Hospital.find(query).to_list()
    
    # Add occupancy data
    result = []
    for hospital in hospitals:
        result.append({
            "id": str(hospital.id),
            "name": hospital.name,
            "city": hospital.city,
            "state": hospital.state,
            "address": hospital.address,
            "phone": hospital.phone,
            "specializations": hospital.specializations,
            "capacity": hospital.capacity,
            "occupancy": hospital.get_occupancy_percentage(),
            "load_probability": hospital.get_load_probability(),
            "subscription_plan": hospital.subscription.get("plan", "free")
        })
    
    return {"hospitals": result, "count": len(result)}


@router.get("/nearby")
async def find_nearby_hospitals(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(10, description="Search radius in kilometers")
):
    """
    Find hospitals near a location using geospatial query
    """
    # MongoDB geospatial query
    # Convert km to meters (MongoDB uses meters)
    radius_meters = radius_km * 1000
    
    hospitals = await Hospital.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius_meters
            }
        }
    }).to_list()
    
    result = []
    for hospital in hospitals:
        result.append({
            "id": str(hospital.id),
            "name": hospital.name,
            "city": hospital.city,
            "address": hospital.address,
            "phone": hospital.phone,
            "location": hospital.location,
            "specializations": hospital.specializations,
            "capacity": hospital.capacity,
            "occupancy": hospital.get_occupancy_percentage(),
            "load_probability": hospital.get_load_probability()
        })
    
    return {"hospitals": result, "count": len(result)}


@router.get("/{hospital_id}")
async def get_hospital_details(hospital_id: str):
    """
    Get detailed hospital information
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        return {
            "id": str(hospital.id),
            "name": hospital.name,
            "city": hospital.city,
            "state": hospital.state,
            "address": hospital.address,
            "pincode": hospital.pincode,
            "phone": hospital.phone,
            "email": hospital.email,
            "location": hospital.location,
            "specializations": hospital.specializations,
            "capacity": hospital.capacity,
            "occupancy": hospital.get_occupancy_percentage(),
            "load_probability": hospital.get_load_probability(),
            "subscription": hospital.subscription
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{hospital_id}/capacity")
async def update_capacity(
    hospital_id: str,
    capacity_update: dict,
    current_user: User = Depends(get_hospital_user)
):
    """
    Update hospital bed/ICU/ventilator capacity
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Verify ownership
        if hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update capacity
        hospital.capacity.update(capacity_update)
        hospital.updated_at = datetime.utcnow()
        await hospital.save()
        
        logger.info(f"Updated capacity for hospital {hospital_id}")
        
        return {
            "message": "Capacity updated successfully",
            "capacity": hospital.capacity,
            "occupancy": hospital.get_occupancy_percentage()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{hospital_id}/surge-predictions")
async def get_surge_predictions(
    hospital_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Get AI surge predictions for hospital
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Verify ownership
        if hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check subscription
        if hospital.subscription.get("plan") != "paid":
            raise HTTPException(
                status_code=403,
                detail="Surge predictions available only for paid tier"
            )
        
        # Get recent predictions
        predictions = await SurgePrediction.find(
            SurgePrediction.hospital_id == hospital.id
        ).sort(-SurgePrediction.prediction_date).limit(10).to_list()
        
        return {
            "predictions": [
                {
                    "id": str(p.id),
                    "prediction_date": p.prediction_date,
                    "predicted_patient_count": p.predicted_patient_count,
                    "confidence_score": p.confidence_score,
                    "factors": p.factors,
                    "recommendations": p.recommendations
                }
                for p in predictions
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/health-forecast")
async def get_my_health_forecast(
    current_user: User = Depends(get_hospital_user)
):
    """
    Get 7-day health forecast for the current user's hospital
    """
    try:
        hospital = await Hospital.find_one(Hospital.user_id == current_user.id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital profile not found")
            
        return await ai_service.get_health_forecast(hospital.city)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{hospital_id}/inventory")
async def get_inventory(
    hospital_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Get hospital inventory list
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital or hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        inventory_items = await Inventory.find(
            Inventory.hospital_id == hospital.id
        ).to_list()
        
        return {
            "items": [
                {
                    "id": str(item.id),
                    "item_name": item.item_name,
                    "category": item.category,
                    "current_stock": item.current_stock,
                    "reorder_threshold": item.reorder_threshold,
                    "unit_price": item.unit_price,
                    "is_low_stock": item.is_low_stock(),
                    "last_reorder_date": item.last_reorder_date
                }
                for item in inventory_items
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{hospital_id}/inventory")
async def add_inventory_item(
    hospital_id: str,
    item_data: dict,
    current_user: User = Depends(get_hospital_user)
):
    """
    Add new inventory item
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital or hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        item = Inventory(
            hospital_id=hospital.id,
            **item_data
        )
        await item.insert()
        
        return {
            "message": "Inventory item added",
            "item_id": str(item.id)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{hospital_id}/referrals")
async def get_referrals(
    hospital_id: str,
    direction: str = Query("incoming", regex="^(incoming|outgoing)$"),
    current_user: User = Depends(get_hospital_user)
):
    """
    Get hospital referrals (incoming or outgoing)
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital or hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if direction == "incoming":
            referrals = await Referral.find(
                Referral.to_hospital_id == hospital.id
            ).to_list()
        else:
            referrals = await Referral.find(
                Referral.from_hospital_id == hospital.id
            ).to_list()
        
        return {
            "referrals": [
                {
                    "id": str(r.id),
                    "patient_id": str(r.patient_id),
                    "from_hospital_id": str(r.from_hospital_id),
                    "to_hospital_id": str(r.to_hospital_id),
                    "status": r.status,
                    "reason": r.reason,
                    "payment": r.payment,
                    "created_at": r.created_at
                }
                for r in referrals
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{hospital_id}/referrals/{referral_id}/accept")
async def accept_referral(
    hospital_id: str,
    referral_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Accept incoming referral
    """
    try:
        referral = await Referral.get(ObjectId(referral_id))
        
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        if str(referral.to_hospital_id) != hospital_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        referral.status = ReferralStatus.ACCEPTED
        referral.updated_at = datetime.utcnow()
        await referral.save()
        
        return {"message": "Referral accepted", "status": referral.status}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{hospital_id}/referrals/{referral_id}/reject")
async def reject_referral(
    hospital_id: str,
    referral_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Reject incoming referral
    """
    try:
        referral = await Referral.get(ObjectId(referral_id))
        
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        if str(referral.to_hospital_id) != hospital_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        referral.status = ReferralStatus.REJECTED
        referral.updated_at = datetime.utcnow()
        await referral.save()
        
        return {"message": "Referral rejected", "status": referral.status}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{hospital_id}/wallet")
async def get_wallet_details(
    hospital_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Get wallet balance and details
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital or hospital.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital.id)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Get recent transactions
        transactions = await WalletTransaction.find(
            WalletTransaction.wallet_id == wallet.id
        ).sort(-WalletTransaction.created_at).limit(20).to_list()
        
        return {
            "balance": wallet.balance,
            "total_earned": wallet.total_earned,
            "total_withdrawn": wallet.total_withdrawn,
            "recent_transactions": [
                {
                    "id": str(t.id),
                    "type": t.transaction_type,
                    "amount": t.amount,
                    "description": t.description,
                    "created_at": t.created_at
                }
                for t in transactions
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
