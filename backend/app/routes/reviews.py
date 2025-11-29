from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.review import Review
from app.models.hospital import Hospital
from app.models.user import User
from app.middleware.auth import get_patient_user
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class CreateReviewRequest(BaseModel):
    hospital_id: str
    rating: int
    comment: Optional[str] = None

@router.post("/")
async def create_review(
    review_data: CreateReviewRequest,
    current_user: User = Depends(get_patient_user)
):
    try:
        if not current_user.profile_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have a patient profile."
            )
        
        hospital_id = ObjectId(review_data.hospital_id)
        patient_id = ObjectId(current_user.profile_id)
        
        hospital = await Hospital.get(hospital_id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
            
        # Check if already reviewed
        existing = await Review.find_one(
            Review.hospital_id == hospital_id,
            Review.patient_id == patient_id
        )
        
        if existing:
            raise HTTPException(status_code=400, detail="You have already reviewed this hospital")
            
        review = Review(
            hospital_id=hospital_id,
            patient_id=patient_id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        await review.insert()
        
        # Update hospital average rating
        reviews = await Review.find(Review.hospital_id == hospital_id).to_list()
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
        hospital.rating = avg_rating
        hospital.review_count = len(reviews)
        await hospital.save()
        
        return {"message": "Review submitted successfully", "review_id": str(review.id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hospital/{hospital_id}")
async def get_hospital_reviews(hospital_id: str):
    try:
        reviews = await Review.find(
            Review.hospital_id == ObjectId(hospital_id)
        ).sort("-created_at").to_list()
        
        return {
            "reviews": [
                {
                    "id": str(r.id),
                    "rating": r.rating,
                    "comment": r.comment,
                    "created_at": r.created_at.isoformat()
                }
                for r in reviews
            ],
            "count": len(reviews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
