from openai import OpenAI
from app.config import settings
from app.models.hospital import Hospital
from app.models.surge_prediction import SurgePrediction
from app.models.capacity_log import CapacityLog
from typing import Dict, List
from bson import ObjectId
from datetime import datetime, timedelta
import json
import logging
import httpx

logger = logging.getLogger(__name__)


class AIService:
    """Service for OpenAI-powered predictions and recommendations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    async def fetch_weather_data(self, city: str) -> Dict:
        """Fetch weather data from OpenWeatherMap API"""
        try:
            # Using OpenWeatherMap API (you'll need to add API key to settings)
            api_key = getattr(settings, 'openweather_api_key', 'demo')
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},IN&appid={api_key}&units=metric"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": data['list'][0]['main']['temp'],
                        "description": data['list'][0]['weather'][0]['description'],
                        "humidity": data['list'][0]['main']['humidity']
                    }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
        
        return {"temperature": 25, "description": "Clear", "humidity": 60}
    
    async def fetch_pollution_data(self, city: str) -> Dict:
        """Fetch pollution data (AQI)"""
        try:
            # Mock AQI data - in production, integrate with IQAir or similar
            # For demo, we'll generate seasonal values
            month = datetime.now().month
            # Winter months (Nov-Feb) have higher pollution in India
            if month in [11, 12, 1, 2]:
                aqi = 250 + (month * 10)  # Higher pollution
            else:
                aqi = 100 + (month * 5)   # Moderate pollution
                
            return {
                "aqi": min(aqi, 500),
                "category": "Unhealthy" if aqi > 200 else "Moderate" if aqi > 100 else "Good"
            }
        except Exception as e:
            logger.error(f"Pollution API error: {e}")
        
        return {"aqi": 150, "category": "Moderate"}
    
    def get_upcoming_festivals(self) -> List[Dict]:
        """Get upcoming festivals for next 14 days"""
        festivals_2025 = {
            "2025-01-14": "Makar Sankranti",
            "2025-01-26": "Republic Day",
            "2025-03-14": "Holi",
            "2025-03-30": "Ram Navami",
            "2025-08-15": "Independence Day",
            "2025-08-27": "Ganesh Chaturthi",
            "2025-10-02": "Gandhi Jayanti",
            "2025-10-12": "Dussehra",
            "2025-11-01": "Diwali",
            "2025-11-15": "Guru Nanak Jayanti",
            "2025-12-25": "Christmas"
        }
        
        today = datetime.now().date()
        upcoming = []
        
        for date_str, festival in festivals_2025.items():
            festival_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            days_until = (festival_date - today).days
            
            if 0 <= days_until <= 14:
                upcoming.append({
                    "name": festival,
                    "date": date_str,
                    "days_until": days_until
                })
        
        return upcoming
    
    async def get_historical_trend(self, hospital_id: ObjectId) -> Dict:
        """Analyze historical capacity trends"""
        try:
            # Get last 30 days of capacity logs
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            logs = await CapacityLog.find(
                CapacityLog.hospital_id == hospital_id,
                CapacityLog.timestamp >= thirty_days_ago
            ).sort("-timestamp").limit(30).to_list()
            
            if not logs:
                return {"trend": "No data", "avg_occupancy": 0}
            
            occupancy_rates = []
            for log in logs:
                total = log.capacity.get('total_beds', 1)
                available = log.capacity.get('available_beds', 0)
                occupancy = ((total - available) / total * 100) if total > 0 else 0
                occupancy_rates.append(occupancy)
            
            avg_occupancy = sum(occupancy_rates) / len(occupancy_rates)
            
            # Determine trend
            if avg_occupancy > 80:
                trend = "High demand - consistently near capacity"
            elif avg_occupancy > 60:
                trend = "Moderate demand - steady patient flow"
            else:
                trend = "Low demand - below average occupancy"
            
            return {
                "trend": trend,
                "avg_occupancy": round(avg_occupancy, 2),
                "recent_logs": len(logs)
            }
        except Exception as e:
            logger.error(f"Historical trend error: {e}")
            return {"trend": "Stable", "avg_occupancy": 50}
    
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

    async def generate_autonomous_plan(self, prediction: Dict) -> Dict:
        """
        Agentic AI: Generate autonomous resource reallocation plan based on predictions.
        This simulates the 'Proactive Preparation Phase'.
        """
        try:
            prompt = f"""
            As an Autonomous Hospital Management Agent, analyze this surge prediction and generate a proactive resource reallocation plan.
            
            Prediction: {json.dumps(prediction)}
            
            Output JSON format:
            {{
                "actions": [
                    {{
                        "type": "staffing" | "inventory" | "capacity",
                        "action": "Specific action description",
                        "priority": "high" | "medium" | "low",
                        "auto_executable": boolean
                    }}
                ],
                "reasoning": "Brief explanation of the strategy"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert autonomous hospital operations agent."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Agentic plan generation failed: {e}")
            return {
                "actions": [
                    {
                        "type": "general",
                        "action": "Monitor situation closely",
                        "priority": "medium",
                        "auto_executable": False
                    }
                ],
                "reasoning": "Fallback plan due to AI service error"
            }

    async def get_health_assistant_response(self, message: str, history: List[Dict]) -> str:
        """
        AI Health Assistant for patients
        """
        try:
            # Check if API key is available
            if not settings.openai_api_key or "your-openai-api-key" in settings.openai_api_key:
                logger.error("OpenAI API key not configured properly. Please check your .env file.")
                return "I apologize, but the AI assistant is currently not configured. Please contact support."
            
            system_prompt = """
            You are HealthEase AI, a helpful medical assistant. 
            Your goal is to help patients find the right care.
            - If they describe symptoms, suggest potential causes but ALWAYS advise seeing a doctor.
            - Recommend what kind of specialist they should see (e.g., "You should see a Cardiologist").
            - Keep answers concise and empathetic.
            - Do not provide definitive medical diagnoses.
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            # Ensure history has valid roles
            valid_history = [msg for msg in history if msg.get('role') in ['user', 'assistant']]
            messages.extend(valid_history)
            messages.append({"role": "user", "content": message})
            
            logger.info(f"Making OpenAI API call with key ending in '...{settings.openai_api_key[-4:]}'")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            
            # Check for specific OpenAI authentication error
            if "AuthenticationError" in str(type(e)):
                 logger.error("OpenAI API request failed with an AuthenticationError. This strongly suggests the API key is invalid, expired, or has been revoked. Please verify the key in your .env file.")
                 return "I'm sorry, but there seems to be an issue with my connection to the AI service (Authentication Error). The API key may be invalid. Please contact support."

            # Provide helpful fallback responses based on common medical queries
            if any(word in message.lower() for word in ['fever', 'temperature', 'cold']):
                return "For fever and cold symptoms, I recommend: 1) Rest and stay hydrated, 2) Monitor your temperature, 3) If fever persists over 3 days or is very high, see a General Physician immediately."
            elif any(word in message.lower() for word in ['chest', 'heart', 'pain']):
                return "For any chest pain or heart-related symptoms, please see a Cardiologist immediately or go to the emergency room. Don't delay seeking medical attention."
            elif any(word in message.lower() for word in ['stomach', 'abdomen', 'nausea']):
                return "For stomach or abdominal issues, consider seeing a Gastroenterologist. If symptoms are severe or persistent, seek medical attention promptly."
            else:
                return "I apologize, but I'm having trouble processing your request right now. For any health concerns, I recommend consulting with a healthcare professional or visiting our hospital search to find appropriate specialists."


# Global AI service instance
ai_service = AIService()
