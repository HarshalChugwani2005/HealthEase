from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId

class Review(Document):
    hospital_id: ObjectId = Field(index=True)
    patient_id: ObjectId = Field(index=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reviews"
