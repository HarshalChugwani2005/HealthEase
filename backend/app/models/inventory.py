from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum


class InventoryCategory(str, Enum):
    """Inventory category enumeration"""
    MEDICINE = "medicine"
    EQUIPMENT = "equipment"
    CONSUMABLE = "consumable"


class Inventory(Document):
    """Inventory management model"""
    hospital_id: ObjectId = Field(index=True)
    item_name: str
    category: InventoryCategory
    current_stock: int = 0
    reorder_threshold: int = 0
    unit_price: float = 0.0
    last_reorder_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "inventory"
        indexes = [
            "hospital_id",
            "category",
            "current_stock"
        ]
    
    def is_low_stock(self) -> bool:
        """Check if item is below reorder threshold"""
        return self.current_stock < self.reorder_threshold
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Paracetamol 500mg",
                "category": "medicine",
                "current_stock": 150,
                "reorder_threshold": 50
            }
        }
