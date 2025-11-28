from beanie import Document
from pydantic import Field
from datetime import datetime
from beanie import PydanticObjectId as ObjectId


class CapacityLog(Document):
    """Real-time capacity logging for analytics"""
    hospital_id: ObjectId = Field(index=True)
    beds_occupied: int
    icu_occupied: int
    ventilators_occupied: int
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        name = "capacity_logs"
        indexes = [
            "hospital_id",
            "timestamp",
            [("hospital_id", 1), ("timestamp", -1)]
        ]
        # TTL index to auto-delete logs older than 30 days
        timeseries = {
            "time_field": "timestamp",
            "meta_field": "hospital_id",
            "granularity": "hours"
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "beds_occupied": 45,
                "icu_occupied": 8,
                "ventilators_occupied": 3
            }
        }
