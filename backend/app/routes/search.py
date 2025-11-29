from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.hospital import Hospital
from app.middleware.auth import get_current_user
from typing import Optional, List
from bson import ObjectId
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Hospital Search"])


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return round(distance, 2)


@router.get("/hospitals")
async def search_hospitals(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    max_distance_km: int = Query(50, description="Maximum distance in km"),
    specialization: Optional[str] = Query(None, description="Required specialization"),
    has_beds: bool = Query(True, description="Filter hospitals with available beds"),
    has_icu: bool = Query(False, description="Filter hospitals with available ICU"),
    has_ventilator: bool = Query(False, description="Filter hospitals with ventilators"),
    sort_by: str = Query("distance", description="Sort by: distance, beds, rating"),
    limit: int = Query(20, description="Maximum results")
):
    """
    Smart hospital search with geolocation
    - Finds nearby hospitals
    - Filters by specialization, bed availability
    - Calculates distance and travel time
    - Shows real-time capacity
    """
    try:
        # Get all hospitals
        all_hospitals = await Hospital.find_all().to_list()
        
        results = []
        
        for hospital in all_hospitals:
            # Skip hospitals without coordinates
            if not hospital.location or "coordinates" not in hospital.location:
                continue
            
            h_lon, h_lat = hospital.location["coordinates"]
            
            # Calculate distance
            distance = calculate_distance(
                latitude, longitude,
                h_lat, h_lon
            )
            
            # Filter by max distance
            if distance > max_distance_km:
                continue
            
            # Filter by specialization
            if specialization and specialization not in hospital.specializations:
                continue
            
            # Filter by bed availability
            available_beds = hospital.capacity.get('available_beds', 0)
            if has_beds and available_beds <= 0:
                continue
            
            # Filter by ICU
            available_icu = hospital.capacity.get('icu_beds', 0)
            if has_icu and available_icu <= 0:
                continue
            
            # Filter by ventilator
            available_ventilators = hospital.capacity.get('ventilators', 0)
            if has_ventilator and available_ventilators <= 0:
                continue
            
            # Calculate travel time (assuming average speed 40 km/h in city)
            travel_time_minutes = int((distance / 40) * 60)
            
            # Calculate occupancy (dict with beds/icu/ventilators)
            occupancy = hospital.get_occupancy_percentage()
            # Use an average occupancy value for status computation
            occ_values = [v for v in occupancy.values() if isinstance(v, (int, float))]
            avg_occupancy = sum(occ_values) / len(occ_values) if occ_values else 0
            
            # Determine status
            if avg_occupancy >= 95:
                status_text = "Critical"
                status_color = "red"
            elif avg_occupancy >= 80:
                status_text = "High Occupancy"
                status_color = "orange"
            elif avg_occupancy >= 60:
                status_text = "Moderate"
                status_color = "yellow"
            else:
                status_text = "Available"
                status_color = "green"
            
            results.append({
                "id": str(hospital.id),
                "name": hospital.name,
                "address": hospital.address,
                "city": hospital.city,
                "state": hospital.state,
                "phone": hospital.phone,
                "email": hospital.email,
                "specializations": hospital.specializations,
                "distance_km": distance,
                "travel_time_minutes": travel_time_minutes,
                "coordinates": {
                    "latitude": h_lat,
                    "longitude": h_lon
                },
                "capacity": {
                    "total_beds": hospital.capacity.get('total_beds', 0),
                    "available_beds": available_beds,
                    "occupied_beds": hospital.capacity.get('occupied_beds', 0),
                    "icu_beds": available_icu,
                    "ventilators": available_ventilators,
                    "occupancy_percentage": occupancy
                },
                "status": {
                    "text": status_text,
                    "color": status_color
                },
                "subscription_tier": hospital.subscription.get("plan", "free"),
                "is_verified": getattr(hospital, "is_verified", False),
                "rating": 4.5  # Placeholder - implement reviews later
            })
        
        # Sort results
        if sort_by == "distance":
            results.sort(key=lambda x: x['distance_km'])
        elif sort_by == "beds":
            results.sort(key=lambda x: x['capacity']['available_beds'], reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x['rating'], reverse=True)
        
        # Limit results
        results = results[:limit]
        
        logger.info(f"Found {len(results)} hospitals near ({latitude}, {longitude})")
        
        return {
            "query": {
                "latitude": latitude,
                "longitude": longitude,
                "max_distance_km": max_distance_km,
                "specialization": specialization,
                "filters": {
                    "has_beds": has_beds,
                    "has_icu": has_icu,
                    "has_ventilator": has_ventilator
                }
            },
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Hospital search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/hospitals/{hospital_id}/details")
async def get_hospital_details(hospital_id: str):
    """
    Get detailed information about a specific hospital
    """
    try:
        hospital = await Hospital.get(ObjectId(hospital_id))
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        occupancy = hospital.get_occupancy_percentage()
        
        return {
            "id": str(hospital.id),
            "name": hospital.name,
            "address": hospital.address,
            "city": hospital.city,
            "state": hospital.state,
            "phone": hospital.phone,
            "email": hospital.email,
            "registration_number": hospital.registration_number,
            "specializations": hospital.specializations,
            "coordinates": {
                "latitude": hospital.location["coordinates"][1] if hospital.location else None,
                "longitude": hospital.location["coordinates"][0] if hospital.location else None
            },
            "capacity": {
                "total_beds": hospital.capacity.get('total_beds', 0),
                "available_beds": hospital.capacity.get('available_beds', 0),
                "occupied_beds": hospital.capacity.get('occupied_beds', 0),
                "icu_beds": hospital.capacity.get('icu_beds', 0),
                "ventilators": hospital.capacity.get('ventilators', 0),
                "occupancy_percentage": occupancy
            },
            "subscription": {
                "tier": hospital.subscription.get("plan", "free"),
                "expiry": hospital.subscription.get("expires_at").isoformat() if hospital.subscription.get("expires_at") else None
            },
            "verification": {
                "is_verified": getattr(hospital, "is_verified", False),
                "verified_at": getattr(hospital, "verified_at", None).isoformat() if getattr(hospital, "verified_at", None) else None
            },
            "created_at": hospital.created_at.isoformat(),
            "rating": 4.5  # Placeholder
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get hospital details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/nearby-hospitals")
async def get_nearby_hospitals_simple(
    city: str = Query(..., description="City name"),
    limit: int = Query(10, description="Maximum results")
):
    """
    Simplified search by city (for users without GPS)
    """
    try:
        hospitals = await Hospital.find(
            Hospital.city == city
        ).to_list()
        
        results = []
        
        for hospital in hospitals[:limit]:
            occupancy = hospital.get_occupancy_percentage()
            available_beds = hospital.capacity.get('available_beds', 0)
            
            results.append({
                "id": str(hospital.id),
                "name": hospital.name,
                "address": hospital.address,
                "phone": hospital.phone,
                "specializations": hospital.specializations,
                "available_beds": available_beds,
                "occupancy_percentage": occupancy,
                "has_capacity": available_beds > 0
            })
        
        # Sort by available beds
        results.sort(key=lambda x: x['available_beds'], reverse=True)
        
        return {
            "city": city,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"City search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/specializations")
async def get_all_specializations():
    """
    Get list of all available specializations
    """
    try:
        hospitals = await Hospital.find_all().to_list()
        
        specializations = set()
        for hospital in hospitals:
            specializations.update(hospital.specializations)
        
        return {
            "specializations": sorted(list(specializations)),
            "count": len(specializations)
        }
        
    except Exception as e:
        logger.error(f"Get specializations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
