from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.user import User
from app.middleware.auth import get_current_user
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class CreateNotificationRequest(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None

@router.get("/")
async def get_notifications(
    status: Optional[NotificationStatus] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get notifications for current user"""
    try:
        # Note: This uses the User's own ID, not a profile ID, as notifications are user-centric.
        user_id = current_user.id
        query_conditions = [Notification.user_id == user_id]
        
        if status:
            query_conditions.append(Notification.status == status)
            
        notifications = await Notification.find(*query_conditions).sort(
            "-created_at"
        ).skip(skip).limit(limit).to_list()
        
        return {
            "notifications": [
                {
                    "id": str(n.id),
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "data": n.data,
                    "status": n.status,
                    "created_at": n.created_at.isoformat(),
                    "read_at": n.read_at.isoformat() if n.read_at else None
                }
                for n in notifications
            ],
            "count": len(notifications)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        notification = await Notification.get(ObjectId(notification_id))
        if not notification or notification.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
        await notification.save()
        
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete notification"""
    try:
        notification = await Notification.get(ObjectId(notification_id))
        if not notification or notification.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        await notification.delete()
        return {"message": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))