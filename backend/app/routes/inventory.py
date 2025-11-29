from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.inventory import Inventory, InventoryCategory
from app.models.user import User
from app.middleware.auth import get_hospital_user
from bson import ObjectId
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])


class AddItemRequest(BaseModel):
    """Schema for adding inventory item"""
    item_name: str
    category: str
    current_stock: int
    reorder_threshold: int
    unit_price: float = 0.0


class UpdateItemRequest(BaseModel):
    """Schema for updating inventory item"""
    current_stock: Optional[int] = None
    reorder_threshold: Optional[int] = None
    unit_price: Optional[float] = None


@router.get("/list")
async def get_inventory(
    category: Optional[str] = None,
    current_user: User = Depends(get_hospital_user)
):
    """Get inventory list for hospital"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        query_conditions = [Inventory.hospital_id == hospital_id]
        if category:
            query_conditions.append(Inventory.category == category)
        
        items = await Inventory.find(*query_conditions).to_list()
        
        result = []
        for item in items:
            result.append({
                "id": str(item.id),
                "item_name": item.item_name,
                "category": item.category,
                "current_stock": item.current_stock,
                "reorder_threshold": item.reorder_threshold,
                "unit_price": item.unit_price,
                "is_low_stock": item.is_low_stock(),
                "last_reorder_date": item.last_reorder_date.isoformat() if item.last_reorder_date else None,
                "updated_at": item.updated_at.isoformat()
            })
        
        return {
            "items": result,
            "count": len(result),
            "low_stock_count": sum(1 for item in result if item["is_low_stock"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get inventory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/add")
async def add_inventory_item(
    item_data: AddItemRequest,
    current_user: User = Depends(get_hospital_user)
):
    """Add new inventory item"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        # Check if item already exists
        existing = await Inventory.find_one(
            Inventory.hospital_id == hospital_id,
            Inventory.item_name == item_data.item_name
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item already exists. Use update endpoint."
            )
        
        # Create new item
        item = Inventory(
            hospital_id=hospital_id,
            item_name=item_data.item_name,
            category=item_data.category,
            current_stock=item_data.current_stock,
            reorder_threshold=item_data.reorder_threshold,
            unit_price=item_data.unit_price,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await item.insert()
        
        logger.info(f"Added inventory item: {item_data.item_name}")
        
        return {
            "message": "Item added successfully",
            "item_id": str(item.id),
            "item_name": item.item_name,
            "is_low_stock": item.is_low_stock()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add inventory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/update/{item_id}")
async def update_inventory_item(
    item_id: str,
    item_data: UpdateItemRequest,
    current_user: User = Depends(get_hospital_user)
):
    """Update inventory item"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        item = await Inventory.get(ObjectId(item_id))
        
        if not item or item.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Update fields
        if item_data.current_stock is not None:
            item.current_stock = item_data.current_stock
        if item_data.reorder_threshold is not None:
            item.reorder_threshold = item_data.reorder_threshold
        if item_data.unit_price is not None:
            item.unit_price = item_data.unit_price
        
        item.updated_at = datetime.utcnow()
        await item.save()
        
        logger.info(f"Updated inventory item: {item.item_name}")
        
        return {
            "message": "Item updated successfully",
            "item_id": str(item.id),
            "current_stock": item.current_stock,
            "is_low_stock": item.is_low_stock()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update inventory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/alerts")
async def get_inventory_alerts(
    current_user: User = Depends(get_hospital_user)
):
    """Get low stock alerts"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        items = await Inventory.find(Inventory.hospital_id == hospital_id).to_list()
        
        alerts = []
        for item in items:
            if item.is_low_stock():
                alerts.append({
                    "item_id": str(item.id),
                    "item_name": item.item_name,
                    "category": item.category,
                    "current_stock": item.current_stock,
                    "reorder_threshold": item.reorder_threshold,
                    "severity": "critical" if item.current_stock == 0 else "warning"
                })
        
        return {
            "alerts": alerts,
            "count": len(alerts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """Delete inventory item"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        item = await Inventory.get(ObjectId(item_id))
        
        if not item or item.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        await item.delete()
        
        logger.info(f"Deleted inventory item: {item.item_name}")
        
        return {
            "message": "Item deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete inventory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
