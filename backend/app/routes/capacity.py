from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.hospital import Hospital
from app.models.capacity_log import CapacityLog
from app.middleware.auth import get_hospital_user
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/capacity", tags=["Capacity Management"])


class CapacityUpdate(BaseModel):
    """Schema for capacity updates"""
    total_beds: int
    available_beds: int
    icu_beds: int
    available_icu_beds: int
    ventilators: int
    available_ventilators: int


@router.put("/update", response_model=dict)
async def update_capacity(
    capacity_data: CapacityUpdate,
    current_user: dict = Depends(get_hospital_user)
):
    """
    Update hospital capacity in real-time
    Hospital role required
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        hospital = await Hospital.get(hospital_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Validate data
        if capacity_data.available_beds > capacity_data.total_beds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Available beds cannot exceed total beds"
            )
        
        if capacity_data.available_icu_beds > capacity_data.icu_beds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Available ICU beds cannot exceed total ICU beds"
            )
        
        if capacity_data.available_ventilators > capacity_data.ventilators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Available ventilators cannot exceed total ventilators"
            )
        
        # Update hospital capacity
        hospital.capacity = {
            "total_beds": capacity_data.total_beds,
            "available_beds": capacity_data.available_beds,
            "icu_beds": capacity_data.icu_beds,
            "available_icu_beds": capacity_data.available_icu_beds,
            "ventilators": capacity_data.ventilators,
            "available_ventilators": capacity_data.available_ventilators
        }
        hospital.updated_at = datetime.utcnow()
        await hospital.save()
        
        # Log capacity change
        # Log capacity change
        capacity_log = CapacityLog(
            hospital_id=hospital_id,
            beds_occupied=hospital.capacity['total_beds'] - hospital.capacity['available_beds'],
            icu_occupied=hospital.capacity['icu_beds'] - hospital.capacity['available_icu_beds'],
            ventilators_occupied=hospital.capacity['ventilators'] - hospital.capacity['available_ventilators'],
            timestamp=datetime.utcnow()
        )
        await capacity_log.insert()
        
        logger.info(f"Capacity updated for hospital {hospital_id}")
        
        return {
            "message": "Capacity updated successfully",
            "hospital_id": str(hospital_id),
            "capacity": hospital.capacity,
            "occupancy_percentage": hospital.get_occupancy_percentage(),
            "load_probability": hospital.get_load_probability()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Capacity update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/current", response_model=dict)
async def get_current_capacity(
    current_user: dict = Depends(get_hospital_user)
):
    """
    Get current capacity for logged-in hospital
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
            
        hospital_id = ObjectId(current_user.hospital_id)
        hospital = await Hospital.get(hospital_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        return {
            "hospital_id": str(hospital_id),
            "hospital_name": hospital.name,
            "capacity": hospital.capacity,
            "occupancy_percentage": hospital.get_occupancy_percentage(),
            "load_probability": hospital.get_load_probability(),
            "updated_at": hospital.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get capacity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logs")
async def get_capacity_logs(
    days: int = 30,
    current_user: dict = Depends(get_hospital_user)
):
    """
    Get capacity change logs for analysis
    """
    try:
        hospital_id = ObjectId(current_user.hospital_id)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = await CapacityLog.find(
            CapacityLog.hospital_id == hospital_id,
            CapacityLog.timestamp >= start_date
        ).sort("-timestamp").to_list()
        
        # Get current hospital capacity for totals (approximation for historical data)
        hospital = await Hospital.get(hospital_id)
        current_total_beds = hospital.capacity.get('total_beds', 1)
        
        # Calculate statistics
        occupancy_rates = []
        for log in logs:
            occupancy = (log.beds_occupied / current_total_beds * 100) if current_total_beds > 0 else 0
            occupancy_rates.append(occupancy)
        
        avg_occupancy = sum(occupancy_rates) / len(occupancy_rates) if occupancy_rates else 0
        max_occupancy = max(occupancy_rates) if occupancy_rates else 0
        min_occupancy = min(occupancy_rates) if occupancy_rates else 0
        
        return {
            "hospital_id": str(hospital_id),
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "beds_occupied": log.beds_occupied,
                    "icu_occupied": log.icu_occupied,
                    "ventilators_occupied": log.ventilators_occupied,
                    "occupancy_percentage": round(
                        (log.beds_occupied / current_total_beds * 100) if current_total_beds > 0 else 0,
                        2
                    )
                }
                for log in logs
            ],
            "statistics": {
                "avg_occupancy": round(avg_occupancy, 2),
                "max_occupancy": round(max_occupancy, 2),
                "min_occupancy": round(min_occupancy, 2),
                "total_logs": len(logs)
            }
        }
        
    except Exception as e:
        logger.error(f"Capacity logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/quick-update")
async def quick_capacity_update(
    bed_change: int = 0,
    icu_change: int = 0,
    ventilator_change: int = 0,
    current_user: dict = Depends(get_hospital_user)
):
    """
    Quick capacity update by increment/decrement
    Positive values = more available (patient discharged)
    Negative values = less available (patient admitted)
    """
    try:
        hospital_id = ObjectId(current_user.hospital_id)
        hospital = await Hospital.get(hospital_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Update available counts
        new_available_beds = hospital.capacity.get('available_beds', 0) + bed_change
        new_available_icu = hospital.capacity.get('available_icu_beds', 0) + icu_change
        new_available_ventilators = hospital.capacity.get('available_ventilators', 0) + ventilator_change
        
        # Validate bounds
        if new_available_beds < 0 or new_available_beds > hospital.capacity.get('total_beds', 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bed count after update"
            )
        
        if new_available_icu < 0 or new_available_icu > hospital.capacity.get('icu_beds', 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ICU bed count after update"
            )
        
        if new_available_ventilators < 0 or new_available_ventilators > hospital.capacity.get('ventilators', 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ventilator count after update"
            )
        
        # Update
        hospital.capacity['available_beds'] = new_available_beds
        hospital.capacity['available_icu_beds'] = new_available_icu
        hospital.capacity['available_ventilators'] = new_available_ventilators
        hospital.updated_at = datetime.utcnow()
        await hospital.save()
        
        # Log change
        # Log change
        capacity_log = CapacityLog(
            hospital_id=hospital_id,
            beds_occupied=hospital.capacity['total_beds'] - hospital.capacity['available_beds'],
            icu_occupied=hospital.capacity['icu_beds'] - hospital.capacity['available_icu_beds'],
            ventilators_occupied=hospital.capacity['ventilators'] - hospital.capacity['available_ventilators'],
            timestamp=datetime.utcnow()
        )
        await capacity_log.insert()
        
        return {
            "message": "Capacity updated successfully",
            "capacity": hospital.capacity,
            "occupancy_percentage": hospital.get_occupancy_percentage()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
