from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum


class ReferralStatus(str, Enum):
    """Referral status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ReferralPayment(dict):
    """Embedded document for payment details"""
    patient_amount: float = 150.0
    platform_fee: float = 40.0
    hospital_share: float = 110.0
    from_hospital_share: float = 0.0
    to_hospital_share: float = 0.0


class Referral(Document):
    """Patient referral model"""
    patient_id: ObjectId = Field(index=True)
    from_hospital_id: ObjectId = Field(index=True)
    to_hospital_id: ObjectId = Field(index=True)
    status: ReferralStatus = ReferralStatus.PENDING
    payment: dict = Field(default_factory=lambda: {
        "patient_amount": 150.0,
        "platform_fee": 40.0,
        "hospital_share": 110.0,
        "from_hospital_share": 0.0,
        "to_hospital_share": 0.0
    })
    reason: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "referrals"
        indexes = [
            "patient_id",
            "from_hospital_id",
            "to_hospital_id",
            "status",
            [("from_hospital_id", 1), ("status", 1)],
            [("to_hospital_id", 1), ("status", 1)]
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Hospital A at full capacity, referring to Hospital B",
                "status": "pending",
                "payment": {
                    "patient_amount": 150.0,
                    "platform_fee": 40.0,
                    "hospital_share": 110.0
                }
            }
        }
