from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum

class NotificationType(str, Enum):
    SURGE_ALERT = "surge_alert"
    APPOINTMENT_REMINDER = "appointment_reminder"
    INVENTORY_LOW = "inventory_low"
    PAYMENT_RECEIVED = "payment_received"
    REFERRAL_UPDATE = "referral_update"
    SYSTEM_ALERT = "system_alert"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"

class Notification(Document):
    user_id: ObjectId = Field(index=True)
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None  # Additional data for the notification
    status: NotificationStatus = NotificationStatus.UNREAD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
            [("user_id", 1), ("status", 1)]
        ]