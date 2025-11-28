from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId as ObjectId


class SurgeFactors(dict):
    """Embedded document for surge prediction factors"""
    weather: Optional[str] = None
    festivals: List[str] = []
    pollution_index: Optional[float] = None
    historical_trend: Optional[str] = None


class SurgeRecommendations(dict):
    """Embedded document for AI recommendations"""
    staff_count: Optional[int] = None
    bed_allocation: Optional[int] = None


class SurgePrediction(Document):
    """AI-powered surge prediction model"""
    hospital_id: ObjectId = Field(index=True)
    prediction_date: datetime = Field(index=True)
    predicted_patient_count: int
    confidence_score: float = 0.0  # 0.0 to 1.0
    factors: dict = Field(default_factory=dict)
    recommendations: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "surge_predictions"
        indexes = [
            "hospital_id",
            "prediction_date",
            [("hospital_id", 1), ("prediction_date", -1)]
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_patient_count": 45,
                "confidence_score": 0.85,
                "factors": {
                    "weather": "Heavy rainfall expected",
                    "festivals": ["Diwali"],
                    "pollution_index": 350
                },
                "recommendations": {
                    "staff_count": 12,
                    "bed_allocation": 30
                }
            }
        }
