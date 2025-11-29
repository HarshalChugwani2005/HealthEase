from beanie import Document, Link
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId as ObjectId


class GeoLocation(dict):
    """GeoJSON Point for MongoDB geospatial queries"""
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class HospitalCapacity(dict):
    """Embedded document for hospital capacity"""
    total_beds: int = 0
    available_beds: int = 0
    icu_beds: int = 0
    available_icu_beds: int = 0
    ventilators: int = 0
    available_ventilators: int = 0


class HospitalSubscription(dict):
    """Embedded document for subscription details"""
    plan: str = "free"  # 'free' or 'paid'
    expires_at: Optional[datetime] = None
    started_at: Optional[datetime] = None


class Hospital(Document):
    """Hospital model with geospatial support"""
    # user_id can be optional for seeded/system-created hospitals
    user_id: Optional[ObjectId] = Field(default=None, index=True)
    name: str
    address: str
    city: str
    state: str
    pincode: str
    location: dict  # GeoJSON Point format
    phone: str
    email: EmailStr
    subscription: dict = Field(default_factory=lambda: {
        "plan": "free",
        "expires_at": None,
        "started_at": None
    })
    capacity: dict = Field(default_factory=lambda: {
        "total_beds": 0,
        "available_beds": 0,
        "icu_beds": 0,
        "available_icu_beds": 0,
        "ventilators": 0,
        "available_ventilators": 0
    })
    rating: float = 0.0
    review_count: int = 0
    specializations: List[str] = []
    wallet_id: Optional[ObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "hospitals"
        indexes = [
            "user_id",
            "city",
            "email",
            [("location", "2dsphere")]  # Geospatial index
        ]
    
    def get_occupancy_percentage(self) -> dict:
        """Calculate occupancy percentages"""
        capacity = self.capacity
        return {
            "beds": round((1 - capacity["available_beds"] / capacity["total_beds"]) * 100, 2) if capacity["total_beds"] > 0 else 0,
            "icu": round((1 - capacity["available_icu_beds"] / capacity["icu_beds"]) * 100, 2) if capacity["icu_beds"] > 0 else 0,
            "ventilators": round((1 - capacity["available_ventilators"] / capacity["ventilators"]) * 100, 2) if capacity["ventilators"] > 0 else 0
        }
    
    def get_load_probability(self) -> str:
        """Get load probability status"""
        occupancy = self.get_occupancy_percentage()
        avg_occupancy = (occupancy["beds"] + occupancy["icu"] + occupancy["ventilators"]) / 3
        
        if avg_occupancy < 50:
            return "low"
        elif avg_occupancy < 75:
            return "medium"
        elif avg_occupancy < 90:
            return "high"
        else:
            return "critical"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "City General Hospital",
                "city": "Mumbai",
                "location": {
                    "type": "Point",
                    "coordinates": [72.8777, 19.0760]  # [longitude, latitude]
                }
            }
        }
