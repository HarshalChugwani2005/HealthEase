from openai import OpenAI
from app.config import settings
from app.models.hospital import Hospital
from app.models.surge_prediction import SurgePrediction
from typing import Dict
from bson import ObjectId
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for OpenAI-powered predictions and recommendations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def predict_surge(
        self,
        hospital_id: ObjectId,
        multimodal_data: Dict
    ) -> SurgePrediction:
        """
        Use OpenAI to predict patient surge based on multimodal data
        
        Args:
            hospital_id: Hospital ObjectId
            multimodal_data: Dict containing weather, festivals, pollution, etc.
            
        Returns:
            SurgePrediction object
        """
        try:
            # Prepare context for AI
            hospital = await Hospital.get(hospital_id)
            
            prompt = f"""
            You are an AI healthcare analytics expert. Predict patient surge for a hospital based on the following data:
            
            Hospital: {hospital.name}
            Location: {hospital.city}, {hospital.state}
            Current Capacity: {hospital.capacity['available_beds']}/{hospital.capacity['total_beds']} beds available
            
            Environmental Factors:
            - Weather: {multimodal_data.get('weather', 'Normal')}
            - Upcoming Festivals: {', '.join(multimodal_data.get('festivals', []))}
            - Pollution Index (AQI): {multimodal_data.get('pollution_index', 100)}
            - Historical Trend: {multimodal_data.get('historical_trend', 'Stable')}
            
            Provide a prediction in JSON format with:
            1. predicted_patient_count: estimated number of patients in next 24-48 hours
            2. confidence_score: 0.0 to 1.0
            3. key_factors: list of main contributing factors
            4. staff_recommendation: recommended additional staff count
            5. bed_allocation_recommendation: recommended bed preparation
            
            Return ONLY valid JSON, no additional text.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a healthcare analytics AI that provides predictions in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse AI response
            prediction_data = json.loads(response.choices[0].message.content)
            
            # Create surge prediction
            surge_prediction = SurgePrediction(
                hospital_id=hospital_id,
                prediction_date=datetime.utcnow(),
                predicted_patient_count=prediction_data.get('predicted_patient_count', 0),
                confidence_score=prediction_data.get('confidence_score', 0.5),
                factors={
                    "weather": multimodal_data.get('weather'),
                    "festivals": multimodal_data.get('festivals', []),
                    "pollution_index": multimodal_data.get('pollution_index'),
                    "historical_trend": multimodal_data.get('historical_trend'),
                    "key_factors": prediction_data.get('key_factors', [])
                },
                recommendations={
                    "staff_count": prediction_data.get('staff_recommendation', 0),
                    "bed_allocation": prediction_data.get('bed_allocation_recommendation', 0)
                }
            )
            
            await surge_prediction.insert()
            logger.info(f"Created surge prediction for hospital {hospital_id}")
            
            return surge_prediction
            
        except Exception as e:
            logger.error(f"Failed to generate surge prediction: {e}")
            # Return fallback prediction
            return SurgePrediction(
                hospital_id=hospital_id,
                prediction_date=datetime.utcnow(),
                predicted_patient_count=20,
                confidence_score=0.3,
                factors=multimodal_data,
                recommendations={"staff_count": 5, "bed_allocation": 10}
            )
    
    async def calculate_referral_split(
        self,
        from_hospital: Hospital,
        to_hospital: Hospital
    ) -> Dict[str, float]:
        """
        AI-powered dynamic split of ₹110 between hospitals
        
        Args:
            from_hospital: Referring hospital
            to_hospital: Accepting hospital
            
        Returns:
            Dict with 'from_hospital_share' and 'to_hospital_share'
        """
        try:
            prompt = f"""
            Calculate a fair revenue split of ₹110 between two hospitals for a patient referral:
            
            Hospital A (Referring):
            - Current Occupancy: {from_hospital.get_occupancy_percentage()['beds']}%
            - Specializations: {', '.join(from_hospital.specializations[:3])}
            
            Hospital B (Accepting):
            - Current Occupancy: {to_hospital.get_occupancy_percentage()['beds']}%
            - Specializations: {', '.join(to_hospital.specializations[:3])}
            
            Factors to consider:
            1. Hospital A is referring due to capacity constraints or lack of specialization
            2. Hospital B is accepting the patient and providing care
            3. Typically, accepting hospital should get higher share (60-70%)
            4. Referring hospital gets smaller share (30-40%) for coordination
            
            Return JSON with:
            - from_hospital_share: amount for Hospital A (₹)
            - to_hospital_share: amount for Hospital B (₹)
            - rationale: brief explanation
            
            Ensure both shares sum to exactly ₹110.
            Return ONLY valid JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a healthcare finance AI that provides fair payment splits in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            split_data = json.loads(response.choices[0].message.content)
            
            logger.info(
                f"AI-calculated referral split: From={split_data['from_hospital_share']}, "
                f"To={split_data['to_hospital_share']}"
            )
            
            return {
                "from_hospital_share": float(split_data['from_hospital_share']),
                "to_hospital_share": float(split_data['to_hospital_share']),
                "rationale": split_data.get('rationale', 'AI-calculated split')
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate AI split: {e}")
            # Fallback to default 40-70 split
            return {
                "from_hospital_share": 44.0,  # 40% of 110
                "to_hospital_share": 66.0,    # 60% of 110
                "rationale": "Default split (40-60)"
            }


# Global AI service instance
ai_service = AIService()
