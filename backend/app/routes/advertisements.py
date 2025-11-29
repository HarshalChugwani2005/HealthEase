from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.advertisement import Advertisement, AdStatus
from app.models.hospital import Hospital
from app.models.user import User
from app.middleware.auth import get_hospital_user, get_admin_user
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ads", tags=["Advertisements"])


class CreateAdRequest(BaseModel):
    """Schema for creating advertisement"""
    title: str
    description: str
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    target_audience: str = "all"  # all, city, state


class UpdateAdRequest(BaseModel):
    """Schema for updating advertisement"""
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/create")
async def create_advertisement(
    ad_data: CreateAdRequest,
    current_user: User = Depends(get_hospital_user)
):
    """
    Create advertisement (Hospital must be on free tier)
    Paid tier hospitals don't need ads - they get priority listing
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        hospital = await Hospital.get(hospital_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Check subscription tier
        if hospital.subscription_tier != "free":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only free-tier hospitals can create ads. Upgrade to paid for priority listing instead."
            )
        
        # Check if hospital already has active ads
        existing_ads = await Advertisement.find(
            Advertisement.hospital_id == hospital_id,
            Advertisement.is_active == True
        ).to_list()
        
        if len(existing_ads) >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 3 active ads allowed per hospital"
            )
        
        # Create advertisement
        ad = Advertisement(
            hospital_id=hospital_id,
            title=ad_data.title,
            description=ad_data.description,
            image_url=ad_data.image_url or "",
            link_url=ad_data.link_url or "",
            target_audience=ad_data.target_audience,
            is_active=True,
            status=AdStatus.PENDING_REVIEW,
            created_at=datetime.utcnow()
        )
        await ad.insert()
        
        logger.info(f"Hospital {hospital_id} created advertisement {ad.id}")
        
        return {
            "message": "Advertisement created successfully. Pending admin review.",
            "ad_id": str(ad.id),
            "status": ad.status,
            "note": "Your ad will be reviewed by admin within 24 hours"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create ad error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-ads")
async def get_my_advertisements(
    current_user: User = Depends(get_hospital_user)
):
    """
    Get all advertisements for current hospital
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        ads = await Advertisement.find(
            Advertisement.hospital_id == hospital_id
        ).sort("-created_at").to_list()
        
        result = []
        for ad in ads:
            ctr = ad.get_ctr()
            
            result.append({
                "id": str(ad.id),
                "title": ad.title,
                "description": ad.description,
                "image_url": ad.image_url,
                "link_url": ad.link_url,
                "target_audience": ad.target_audience,
                "is_active": ad.is_active,
                "status": ad.status,
                "impressions": ad.impressions,
                "clicks": ad.clicks,
                "ctr": ctr,
                "created_at": ad.created_at.isoformat(),
                "updated_at": ad.updated_at.isoformat() if ad.updated_at else None
            })
        
        return {
            "ads": result,
            "count": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get my ads error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{ad_id}")
async def update_advertisement(
    ad_id: str,
    ad_data: UpdateAdRequest,
    current_user: User = Depends(get_hospital_user)
):
    """
    Update advertisement
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        
        if ad.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own ads"
            )
        
        # Update fields
        update_data = ad_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ad, key, value)
        
        # If content changed, reset to pending review
        if ad_data.title or ad_data.description or ad_data.image_url:
            ad.status = AdStatus.PENDING_REVIEW
        
        ad.updated_at = datetime.utcnow()
        await ad.save()
        
        logger.info(f"Updated advertisement {ad_id}")
        
        return {
            "message": "Advertisement updated successfully",
            "ad_id": str(ad.id),
            "status": ad.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update ad error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{ad_id}")
async def delete_advertisement(
    ad_id: str,
    current_user: User = Depends(get_hospital_user)
):
    """
    Delete advertisement
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        
        if ad.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own ads"
            )
        
        await ad.delete()
        
        logger.info(f"Deleted advertisement {ad_id}")
        
        return {
            "message": "Advertisement deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete ad error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/display")
async def display_advertisements(
    city: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 5
) -> List[dict]:
    """
    Display relevant ads to users based on location
    """
    try:
        query = {
            "is_active": True,
            "status": AdStatus.APPROVED
        }
        
        # Fetch ads and associated hospitals
        ads = await Advertisement.find(query).to_list()
        
        if not ads:
            return []
        
        # Filter by location if provided
        if city or state:
            hospital_ids = [ad.hospital_id for ad in ads]
            
            hospital_query = {"_id": {"$in": hospital_ids}}
            if city:
                hospital_query["city"] = city
            if state:
                hospital_query["state"] = state
            
            matching_hospitals = await Hospital.find(hospital_query).to_list()
            matching_hospital_ids = {h.id for h in matching_hospitals}
            
            ads = [ad for ad in ads if ad.hospital_id in matching_hospital_ids]
        
        # Simple randomization for ad rotation
        random.shuffle(ads)
        
        # Increment impressions
        for ad in ads[:limit]:
            ad.impressions += 1
            await ad.save()
        
        # Format response
        result = []
        for ad in ads[:limit]:
            hospital = await Hospital.get(ad.hospital_id)
            result.append({
                "id": str(ad.id),
                "title": ad.title,
                "description": ad.description,
                "image_url": ad.image_url,
                "link_url": f"/ads/click/{ad.id}",  # Trackable link
                "hospital_name": hospital.name if hospital else "Unknown",
                "hospital_city": hospital.city if hospital else ""
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Display ads error: {e}")
        # Return empty list on error to not break frontend
        return []


@router.get("/click/{ad_id}")
async def track_ad_click(ad_id: str):
    """
    Track ad click and redirect to target URL
    """
    try:
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ad not found"
            )
        
        ad.clicks += 1
        await ad.save()
        
        # Redirect to the ad's link URL
        if ad.link_url:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=ad.link_url)
        
        return {"message": "Ad click tracked, but no redirect URL provided."}
        
    except Exception as e:
        logger.error(f"Ad click error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process ad click"
        )


# =================================================
# Admin routes for managing advertisements
# =================================================

@router.get("/admin/pending", response_model=List[dict])
async def get_pending_ads(admin_user: dict = Depends(get_admin_user)):
    """
    Admin: Get all ads pending review
    """
    try:
        pending_ads = await Advertisement.find(
            Advertisement.status == AdStatus.PENDING_REVIEW
        ).to_list()
        
        result = []
        for ad in pending_ads:
            hospital = await Hospital.get(ad.hospital_id)
            result.append({
                "id": str(ad.id),
                "title": ad.title,
                "description": ad.description,
                "hospital_name": hospital.name if hospital else "Unknown",
                "created_at": ad.created_at.isoformat()
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Admin get pending ads error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/approve/{ad_id}")
async def approve_ad(ad_id: str, admin_user: dict = Depends(get_admin_user)):
    """
    Admin: Approve an advertisement
    """
    try:
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        
        ad.status = AdStatus.APPROVED
        ad.is_active = True
        ad.updated_at = datetime.utcnow()
        await ad.save()
        
        logger.info(f"Admin approved ad {ad_id}")
        
        return {"message": "Advertisement approved successfully"}
        
    except Exception as e:
        logger.error(f"Admin approve ad error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/reject/{ad_id}")
async def reject_ad(
    ad_id: str,
    reason: str,
    admin_user: dict = Depends(get_admin_user)
):
    """
    Admin: Reject an advertisement
    """
    try:
        ad = await Advertisement.get(ObjectId(ad_id))
        
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        
        ad.status = AdStatus.REJECTED
        ad.is_active = False
        ad.admin_notes = reason
        ad.updated_at = datetime.utcnow()
        await ad.save()
        
        logger.warning(f"Admin rejected ad {ad_id}. Reason: {reason}")
        
        return {"message": "Advertisement rejected successfully"}
        
    except Exception as e:
        logger.error(f"Admin reject ad error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
