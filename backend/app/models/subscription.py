from beanie import Document
from pydantic import Field
from typing import List
from datetime import datetime


class SubscriptionPlan(Document):
    """Subscription plan model"""
    name: str = Field(unique=True)  # 'Free' or 'Paid'
    monthly_price: float = 0.0
    features: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "subscription_plans"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Paid",
                "monthly_price": 999.0,
                "features": [
                    "AI surge predictions",
                    "Auto inventory reordering during festivals",
                    "Advanced analytics",
                    "Priority support"
                ]
            }
        }
