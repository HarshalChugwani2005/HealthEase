from fastapi import APIRouter, HTTPException, status, Depends
from app.models.hospital import Hospital
from app.models.surge_prediction import SurgePrediction
from app.models.capacity_log import CapacityLog
from app.middleware.auth import get_hospital_user, get_current_user
from app.services.ai_service import AIService
from typing import List
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/surge", tags=["Surge Prediction"])


@router.post("/predict/{hospital_id}")
async def predict_surge(
    hospital_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered surge prediction for a hospital
    Requires admin or hospital role
    """
    # Verify hospital exists
    try:
        hospital_obj_id = ObjectId(hospital_id)
        hospital = await Hospital.get(hospital_obj_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Initialize AI service
        ai_service = AIService()
        
        # Gather multimodal data
        weather_data = await ai_service.fetch_weather_data(hospital.city)
        pollution_data = await ai_service.fetch_pollution_data(hospital.city)
        festivals = ai_service.get_upcoming_festivals()
        historical_trend = await ai_service.get_historical_trend(hospital_obj_id)
        
        multimodal_data = {
            "weather": f"{weather_data['description']}, {weather_data['temperature']}°C",
            "festivals": [f"{f['name']} in {f['days_until']} days" for f in festivals],
            "pollution_index": pollution_data['aqi'],
            "pollution_category": pollution_data['category'],
            "historical_trend": historical_trend['trend'],
            "avg_occupancy": historical_trend['avg_occupancy']
        }
        
        # Generate prediction
        prediction = await ai_service.predict_surge(hospital_obj_id, multimodal_data)
        
        logger.info(f"Generated surge prediction for hospital {hospital_id}")
        
        return {
            "prediction_id": str(prediction.id),
            "hospital_id": hospital_id,
            "hospital_name": hospital.name,
            "predicted_patient_count": prediction.predicted_patient_count,
            "confidence_score": prediction.confidence_score,
            "prediction_date": prediction.prediction_date.isoformat(),
            "factors": prediction.factors,
            "recommendations": prediction.recommendations,
            "environmental_data": multimodal_data
        }
        
    except Exception as e:
        logger.error(f"Surge prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate prediction: {str(e)}"
        )


@router.get("/history/{hospital_id}")
async def get_surge_history(
    hospital_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Get historical surge predictions for a hospital
    """
    try:
        hospital_obj_id = ObjectId(hospital_id)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        predictions = await SurgePrediction.find(
            SurgePrediction.hospital_id == hospital_obj_id,
            SurgePrediction.created_at >= start_date
        ).sort("-created_at").to_list()
        
        return {
            "hospital_id": hospital_id,
            "predictions": [
                {
                    "id": str(p.id),
                    "predicted_patient_count": p.predicted_patient_count,
                    "confidence_score": p.confidence_score,
                    "prediction_date": p.prediction_date.isoformat(),
                    "created_at": p.created_at.isoformat(),
                    "factors": p.factors
                }
                for p in predictions
            ],
            "count": len(predictions)
        }
        
    except Exception as e:
        logger.error(f"Surge history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/dashboard/{hospital_id}")
async def get_surge_dashboard(
    hospital_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive surge dashboard data
    """
    try:
        hospital_obj_id = ObjectId(hospital_id)
        hospital = await Hospital.get(hospital_obj_id)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Get latest prediction
        latest_prediction = await SurgePrediction.find(
            SurgePrediction.hospital_id == hospital_obj_id
        ).sort("-created_at").first_or_none()
        
        # Get capacity trend (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        capacity_logs = await CapacityLog.find(
            CapacityLog.hospital_id == hospital_obj_id,
            CapacityLog.timestamp >= seven_days_ago
        ).sort("timestamp").to_list()
        
        # Calculate trends
        occupancy_trend = []
        for log in capacity_logs:
            total = log.capacity.get('total_beds', 1)
            available = log.capacity.get('available_beds', 0)
            occupancy = ((total - available) / total * 100) if total > 0 else 0
            occupancy_trend.append({
                "timestamp": log.timestamp.isoformat(),
                "occupancy_percentage": round(occupancy, 2)
            })
        
        # Get upcoming festivals
        ai_service = AIService()
        festivals = ai_service.get_upcoming_festivals()
        
        # Current pollution data
        pollution = await ai_service.fetch_pollution_data(hospital.city)
        
        return {
            "hospital_id": hospital_id,
            "hospital_name": hospital.name,
            "current_capacity": hospital.capacity,
            "current_occupancy": hospital.get_occupancy_percentage(),
            "latest_prediction": {
                "predicted_count": latest_prediction.predicted_patient_count if latest_prediction else None,
                "confidence": latest_prediction.confidence_score if latest_prediction else None,
                "date": latest_prediction.prediction_date.isoformat() if latest_prediction else None,
                "recommendations": latest_prediction.recommendations if latest_prediction else {}
            } if latest_prediction else None,
            "occupancy_trend": occupancy_trend,
            "upcoming_festivals": festivals,
            "pollution_alert": {
                "aqi": pollution['aqi'],
                "category": pollution['category'],
                "alert": pollution['aqi'] > 200
            }
        }
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
