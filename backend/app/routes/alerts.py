from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from app.services.ai_service import ai_service
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Health Advisories"])


class HealthAlert(BaseModel):
    """Health alert/advisory model"""
    id: str
    title: str
    type: str  # pollution, festival, epidemic, general
    severity: str  # low, medium, high, critical
    message: str
    affected_regions: List[str]
    recommendations: List[str]
    issued_at: datetime
    expires_at: Optional[datetime] = None


@router.get("/pollution-alerts")
async def get_pollution_alerts(
    city: str = Query("Delhi", description="City name"),
    state: str = Query("Delhi", description="State name")
):
    """
    Get pollution-related health alerts
    Triggers when AQI > 200 (Very Poor/Severe)
    """
    try:
        # Fetch pollution data
        pollution_data = ai_service.fetch_pollution_data(city, state)
        
        if not pollution_data:
            return {
                "has_alert": False,
                "message": "No pollution data available"
            }
        
        aqi = pollution_data.get('aqi', 0)
        
        # Determine severity
        if aqi > 400:
            severity = "critical"
            title = "🚨 SEVERE Air Quality Alert"
            recommendations = [
                "Avoid all outdoor activities",
                "Keep windows and doors closed",
                "Use air purifiers indoors",
                "Wear N95/N99 masks if going outside",
                "High-risk individuals should stay indoors",
                "Monitor health symptoms closely"
            ]
        elif aqi > 300:
            severity = "high"
            title = "⚠️ Very Poor Air Quality Alert"
            recommendations = [
                "Limit outdoor activities to essential only",
                "Wear protective masks (N95)",
                "Children and elderly should stay indoors",
                "Close windows during peak pollution hours",
                "Consult doctor if experiencing breathing issues"
            ]
        elif aqi > 200:
            severity = "medium"
            title = "⚡ Poor Air Quality Advisory"
            recommendations = [
                "Reduce prolonged outdoor activities",
                "Consider wearing masks outdoors",
                "Sensitive groups should limit exposure",
                "Keep medications handy if asthmatic"
            ]
        else:
            return {
                "has_alert": False,
                "aqi": aqi,
                "message": "Air quality is acceptable"
            }
        
        alert = {
            "id": f"pollution_{city}_{datetime.utcnow().strftime('%Y%m%d')}",
            "title": title,
            "type": "pollution",
            "severity": severity,
            "message": f"Air Quality Index (AQI) in {city} is currently {aqi}, which is considered unhealthy. " +
                      f"Primary pollutant: {pollution_data.get('dominant_pollutant', 'PM2.5')}. " +
                      f"Health impacts may be experienced by sensitive groups.",
            "affected_regions": [f"{city}, {state}"],
            "recommendations": recommendations,
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "data": {
                "aqi": aqi,
                "dominant_pollutant": pollution_data.get('dominant_pollutant'),
                "pm25": pollution_data.get('pm25'),
                "pm10": pollution_data.get('pm10')
            }
        }
        
        return {
            "has_alert": True,
            "alert": alert
        }
        
    except Exception as e:
        logger.error(f"Pollution alert error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/festival-health-tips")
async def get_festival_health_tips():
    """
    Get health tips for upcoming festivals
    """
    try:
        festivals = ai_service.get_upcoming_festivals()
        
        if not festivals:
            return {
                "has_tips": False,
                "message": "No major festivals in the next 30 days"
            }
        
        tips_data = []
        
        # Common festival health tips
        festival_recommendations = {
            "Diwali": [
                "Avoid bursting crackers if you have respiratory issues",
                "Wear masks during fireworks",
                "Keep asthma inhalers/medications handy",
                "Avoid overindulgence in sweets if diabetic",
                "Stay hydrated",
                "Monitor air quality before going outdoors"
            ],
            "Holi": [
                "Use natural, organic colors only",
                "Protect eyes and skin before playing",
                "Stay hydrated throughout the day",
                "Avoid color if you have skin allergies",
                "Apply oil/moisturizer before playing with colors",
                "Wash colors off immediately after celebrations"
            ],
            "Durga Puja": [
                "Maintain crowd distancing where possible",
                "Carry hand sanitizers",
                "Wear comfortable footwear to prevent injuries",
                "Stay hydrated in crowded pandals",
                "Monitor children in large crowds"
            ],
            "Eid": [
                "Moderate consumption of festive foods",
                "Maintain hygiene during food preparation",
                "Stay hydrated if fasting",
                "Balance rich foods with fruits and vegetables",
                "Get adequate rest"
            ],
            "Christmas": [
                "Moderate alcohol consumption",
                "Balance festive meals with healthy options",
                "Be cautious with food allergies at parties",
                "Ensure proper food storage",
                "Stay active despite holiday schedule"
            ]
        }
        
        for festival in festivals:
            festival_name = festival['name']
            base_recommendations = festival_recommendations.get(
                festival_name,
                [
                    "Stay hydrated",
                    "Eat balanced meals",
                    "Get adequate rest",
                    "Maintain hygiene",
                    "Monitor health conditions"
                ]
            )
            
            tips_data.append({
                "id": f"festival_{festival_name.replace(' ', '_').lower()}",
                "title": f"🎊 Health Tips for {festival_name}",
                "type": "festival",
                "severity": "low",
                "festival_name": festival_name,
                "festival_date": festival['date'],
                "message": f"With {festival_name} approaching, here are some health precautions to ensure safe celebrations.",
                "recommendations": base_recommendations,
                "issued_at": datetime.utcnow().isoformat()
            })
        
        return {
            "has_tips": True,
            "upcoming_festivals": len(festivals),
            "tips": tips_data
        }
        
    except Exception as e:
        logger.error(f"Festival tips error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/epidemic-alerts")
async def get_epidemic_alerts(
    region: str = Query("India", description="Region/State")
):
    """
    Get epidemic/disease outbreak alerts
    (Placeholder - would integrate with health ministry APIs in production)
    """
    try:
        # Mock epidemic data - in production, integrate with:
        # - Ministry of Health APIs
        # - WHO APIs
        # - State health department feeds
        
        mock_alerts = []
        
        # Example seasonal alerts
        current_month = datetime.utcnow().month
        
        if current_month in [6, 7, 8, 9]:  # Monsoon
            mock_alerts.append({
                "id": "epidemic_dengue_monsoon",
                "title": "🦟 Dengue Fever Alert",
                "type": "epidemic",
                "severity": "high",
                "disease": "Dengue",
                "message": "Monsoon season increases risk of mosquito-borne diseases. " +
                          "Several dengue cases reported in the region.",
                "affected_regions": ["Delhi", "Mumbai", "Kolkata"],
                "recommendations": [
                    "Eliminate stagnant water around homes",
                    "Use mosquito repellents",
                    "Wear full-sleeve clothes",
                    "Seek medical attention for high fever",
                    "Get tested if symptoms persist"
                ],
                "issued_at": datetime.utcnow().isoformat(),
                "prevention": [
                    "Keep surroundings clean",
                    "Cover water storage containers",
                    "Install mosquito nets on windows"
                ]
            })
        
        if current_month in [11, 12, 1, 2]:  # Winter
            mock_alerts.append({
                "id": "epidemic_flu_winter",
                "title": "🤧 Seasonal Influenza Advisory",
                "type": "epidemic",
                "severity": "medium",
                "disease": "Influenza",
                "message": "Seasonal flu cases on the rise. Take preventive measures.",
                "affected_regions": [region],
                "recommendations": [
                    "Get flu vaccination",
                    "Wash hands frequently",
                    "Avoid touching face",
                    "Stay away from sick individuals",
                    "Rest and hydrate if symptomatic"
                ],
                "issued_at": datetime.utcnow().isoformat()
            })
        
        return {
            "has_alerts": len(mock_alerts) > 0,
            "region": region,
            "alerts": mock_alerts,
            "count": len(mock_alerts),
            "note": "Integrate with official health ministry APIs for real-time data"
        }
        
    except Exception as e:
        logger.error(f"Epidemic alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/all-alerts")
async def get_all_alerts(
    city: str = Query("Delhi", description="City name"),
    state: str = Query("Delhi", description="State name")
):
    """
    Get all active health alerts and advisories
    """
    try:
        all_alerts = []
        
        # Pollution alerts
        try:
            pollution_response = await get_pollution_alerts(city, state)
            if pollution_response.get('has_alert'):
                all_alerts.append(pollution_response['alert'])
        except:
            pass
        
        # Festival tips
        try:
            festival_response = await get_festival_health_tips()
            if festival_response.get('has_tips'):
                all_alerts.extend(festival_response['tips'])
        except:
            pass
        
        # Epidemic alerts
        try:
            epidemic_response = await get_epidemic_alerts(state)
            if epidemic_response.get('has_alerts'):
                all_alerts.extend(epidemic_response['alerts'])
        except:
            pass
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        return {
            "location": f"{city}, {state}",
            "total_alerts": len(all_alerts),
            "alerts": all_alerts,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"All alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
