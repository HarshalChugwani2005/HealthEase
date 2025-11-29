from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum


class AdStatus(str, Enum):
    """Advertisement status"""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class AdvertisementMetrics(dict):
    """Embedded document for ad metrics"""
    impressions_count: int = 0
    clicks_count: int = 0


class Advertisement(Document):
    """Advertisement model for free-tier hospitals"""
    hospital_id: ObjectId = Field(index=True)
    title: str
    description: str
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    target_audience: str = "all"  # all, city, state
    is_active: bool = True
    status: AdStatus = AdStatus.PENDING_REVIEW
    impressions: int = 0
    clicks: int = 0
    metrics: dict = Field(default_factory=lambda: {
        "impressions_count": 0,
        "clicks_count": 0
    })
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "advertisements"
        indexes = [
            "hospital_id",
            "is_active",
            [("hospital_id", 1), ("is_active", 1)]
        ]
    
    async def increment_impressions(self):
        """Increment impression count"""
        self.metrics["impressions_count"] += 1
        await self.save()
    
    async def increment_clicks(self):
        """Increment click count"""
        self.metrics["clicks_count"] += 1
        await self.save()
    
    def get_ctr(self) -> float:
        """Calculate click-through rate"""
        if self.metrics["impressions_count"] == 0:
            return 0.0
        return (self.metrics["clicks_count"] / self.metrics["impressions_count"]) * 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Special Cardiology Checkup",
                "description": "Get 20% off on comprehensive cardiac evaluation",
                "link_url": "https://hospital.com/cardiology"
            }
        }
