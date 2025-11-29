import google.generativeai as genai
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
    """Service for Gemini-powered predictions and recommendations"""
    
    def __init__(self):
        # Configure Gemini
        api_key = settings.gemini_api_key or settings.google_maps_api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("Gemini API key not configured. AI features will be disabled.")
            self.model = None
        
    def _rule_based_health_advice(self, message: str) -> str:
        text = (message or "").lower()
        red_flags = [
            (['severe chest pain', 'crushing chest', 'shortness of breath', 'fainting'],
             "This could be an emergency. Please call emergency services or go to the nearest ER immediately."),
            (['stroke', 'face droop', 'slurred speech', 'one side weakness'],
             "Possible stroke symptoms. Seek emergency care immediately."),
            (['severe bleeding', 'uncontrolled bleeding'],
             "Uncontrolled bleeding requires urgent medical attention. Go to an ER now."),
        ]
        for keywords, advice in red_flags:
            if any(k in text for k in keywords):
                return advice

        mappings = [
            (['fever', 'temperature', 'cold', 'cough', 'sore throat'],
             "You may have a viral infection. Rest, hydrate, and monitor temperature. See a General Physician if high fever persists >3 days or symptoms worsen."),
            (['chest pain', 'palpitations', 'breathless', 'shortness of breath'],
             "Please consult a Cardiologist or go to urgent care if symptoms are acute."),
            (['stomach pain', 'abdominal pain', 'nausea', 'vomit', 'diarrhea', 'gastric'],
             "Consider seeing a Gastroenterologist. Start with oral rehydration and light meals; seek care if pain is severe or persistent."),
            (['headache', 'migraine', 'dizziness'],
             "For headaches, ensure hydration, rest, and avoid screen strain. If the headache is the worst you've had or associated with fever/neck stiffness, seek urgent care. A Neurologist can help with persistent migraines."),
            (['back pain', 'joint pain', 'knee pain', 'shoulder pain'],
             "Consider an Orthopedist or Physiotherapist. Gentle mobility and cold/warm compresses can help initially."),
            (['skin rash', 'itching', 'allergy', 'hives'],
             "This could be an allergic or dermatological condition. An Allergist or Dermatologist can help. Consider antihistamines if previously tolerated."),
            (['anxiety', 'low mood', 'stress', 'panic'],
             "A Psychologist or Psychiatrist can help. Practice breathing exercises and seek support if symptoms interfere with daily life."),
        ]
        for keywords, advice in mappings:
            if any(k in text for k in keywords):
                return advice + " This is general guidance, not a diagnosis."
        return "I recommend starting with a General Physician who can assess your symptoms and direct you to the right specialist. This is general guidance, not a diagnosis."
        
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
        Use Gemini to predict patient surge based on multimodal data
        """
        try:
            if not self.model:
                raise ValueError("Gemini not configured")

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
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response (strip markdown if present)
            content = response.text.replace('```json', '').replace('```', '').strip()
            prediction_data = json.loads(content)
            
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
        """
        try:
            if not self.model:
                raise ValueError("Gemini not configured")

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
            
            response = self.model.generate_content(prompt)
            content = response.text.replace('```json', '').replace('```', '').strip()
            split_data = json.loads(content)
            
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
        """
        try:
            if not self.model:
                raise ValueError("Gemini not configured")

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
            Return ONLY valid JSON.
            """
            
            response = self.model.generate_content(prompt)
            content = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
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
            if not self.model:
                return self._rule_based_health_advice(message)
            
            system_prompt = """
            You are HealthEase AI, a helpful medical assistant. 
            Your goal is to help patients find the right care.
            - If they describe symptoms, suggest potential causes but ALWAYS advise seeing a doctor.
            - Recommend what kind of specialist they should see (e.g., "You should see a Cardiologist").
            - Keep answers concise and empathetic.
            - Do not provide definitive medical diagnoses.
            """
            
            # Gemini handles history differently, but we can just append context for now
            # or use start_chat if we want to maintain state properly.
            # For simplicity in this stateless endpoint, we'll construct a prompt.
            
            logger.info("Generating Gemini response for chat...")
            chat = self.model.start_chat(history=[])
            
            # Add system instruction via initial context if needed, or just rely on the prompt
            full_prompt = f"{system_prompt}\n\nUser Message: {message}"
            
            response = chat.send_message(full_prompt)
            logger.info("Gemini response generated successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return self._rule_based_health_advice(message)

    async def get_health_forecast(self, city: str) -> Dict:
        """
        Generate AQI forecast and Plausible Illness Calendar for the next 7 days
        """
        try:
            if not self.model:
                raise ValueError("Gemini not configured")

            prompt = f"""
            Generate a 7-day health forecast for {city}, India.
            Include:
            1. Forecasted AQI (Air Quality Index) for each day (realistic values based on current season).
            2. Plausible illnesses/health risks for each day based on weather/AQI.
            
            Output JSON format:
            {{
                "forecast": [
                    {{
                        "date": "YYYY-MM-DD",
                        "aqi": integer,
                        "aqi_category": "Good" | "Moderate" | "Unhealthy",
                        "illnesses": ["illness1", "illness2"],
                        "precaution": "Brief precaution"
                    }}
                ]
            }}
            Return ONLY valid JSON.
            """
            
            response = self.model.generate_content(prompt)
            content = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Health forecast error: {e}")
            # Fallback data
            today = datetime.now()
            return {
                "forecast": [
                    {
                        "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "aqi": 150,
                        "aqi_category": "Moderate",
                        "illnesses": ["Seasonal Flu", "Allergies"],
                        "precaution": "Wear a mask if sensitive"
                    } for i in range(7)
                ]
            }


# Global AI service instance
ai_service = AIService()
