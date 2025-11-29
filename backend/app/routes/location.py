from fastapi import APIRouter, HTTPException, Request
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/location", tags=["Location Services"])


@router.get("/detect")
async def detect_location(request: Request):
    """
    Detect user location using multiple methods:
    1. Google Geolocation API (if API key available)
    2. IP-based geolocation as fallback
    """
    try:
        # Get client IP
        client_ip = request.client.host
        
        # Try Google Geolocation API first
        if settings.google_maps_api_key and settings.google_maps_api_key != "YOUR_GOOGLE_MAPS_API_KEY_HERE":
            try:
                location = await get_location_via_google(client_ip)
                if location:
                    return {
                        "success": True,
                        "method": "google",
                        "location": location,
                        "accuracy": "high"
                    }
            except Exception as e:
                logger.warning(f"Google Geolocation API failed: {e}")
        
        # Fallback to IP-based geolocation
        location = await get_location_via_ip(client_ip)
        if location:
            return {
                "success": True,
                "method": "ip",
                "location": location,
                "accuracy": "medium"
            }
        
        raise HTTPException(
            status_code=503,
            detail="Unable to detect location using any available method"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Location detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Location detection failed: {str(e)}"
        )


async def get_location_via_google(client_ip: str = None):
    """Use Google Geolocation API"""
    try:
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={settings.google_maps_api_key}"
        
        payload = {"considerIp": True}
        if client_ip and client_ip not in ["127.0.0.1", "localhost"]:
            payload["homeMobileCountryCode"] = 0
            payload["homeMobileNetworkCode"] = 0
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "latitude": data["location"]["lat"],
                    "longitude": data["location"]["lng"],
                    "accuracy_meters": data.get("accuracy", 100)
                }
            else:
                logger.error(f"Google API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Google geolocation error: {e}")
        return None


async def get_location_via_ip(client_ip: str):
    """Use IP-based geolocation (ipapi.co)"""
    try:
        # For localhost, use a default location (Delhi, India)
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            logger.info("Using default location for localhost")
            return {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "city": "Delhi",
                "country": "India",
                "accuracy_meters": 50000
            }
        
        # Use ipapi.co for real IPs
        url = f"https://ipapi.co/{client_ip}/json/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "city": data.get("city"),
                    "region": data.get("region"),
                    "country": data.get("country_name"),
                    "accuracy_meters": 10000  # City-level accuracy
                }
            else:
                logger.error(f"IP API error: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"IP geolocation error: {e}")
        return None


@router.get("/geocode")
async def geocode_address(address: str):
    """
    Convert address to coordinates using Google Geocoding API
    """
    try:
        if not settings.google_maps_api_key or settings.google_maps_api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
            raise HTTPException(
                status_code=501,
                detail="Geocoding service not configured"
            )
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.google_maps_api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "OK" and len(data["results"]) > 0:
                    location = data["results"][0]["geometry"]["location"]
                    return {
                        "success": True,
                        "location": {
                            "latitude": location["lat"],
                            "longitude": location["lng"]
                        },
                        "formatted_address": data["results"][0]["formatted_address"]
                    }
                else:
                    raise HTTPException(
                        status_code=404,
                        detail="Address not found"
                    )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Geocoding service unavailable"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding failed: {str(e)}"
        )
