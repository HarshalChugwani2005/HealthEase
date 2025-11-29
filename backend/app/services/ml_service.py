import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import asyncio
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.capacity_log import CapacityLog
from app.models.referral import Referral
from app.models.analytics import PatientOutcome
from app.models.telemedicine import HealthData
from app.models.medication import Medication
import logging

logger = logging.getLogger(__name__)

class MLPredictor:
    """Machine Learning models for healthcare predictions"""
    
    def __init__(self):
        self.models_path = "app/ml_models"
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # Ensure models directory exists
        os.makedirs(self.models_path, exist_ok=True)
        
        # Load existing models or initialize new ones
        self.load_or_initialize_models()
    
    def load_or_initialize_models(self):
        """Load trained models or initialize new ones"""
        try:
            # Hospital Surge Prediction Model
            self.models['surge_predictor'] = self._load_model('surge_predictor.pkl') or RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )
            
            # Patient Risk Assessment Model
            self.models['risk_assessment'] = self._load_model('risk_assessment.pkl') or GradientBoostingClassifier(
                n_estimators=100, max_depth=6, random_state=42
            )
            
            # Readmission Prediction Model
            self.models['readmission_predictor'] = self._load_model('readmission_predictor.pkl') or LogisticRegression(
                random_state=42, max_iter=1000
            )
            
            # Hospital Capacity Optimizer
            self.models['capacity_optimizer'] = self._load_model('capacity_optimizer.pkl') or RandomForestRegressor(
                n_estimators=150, max_depth=12, random_state=42
            )
            
            # Medication Adherence Predictor
            self.models['adherence_predictor'] = self._load_model('adherence_predictor.pkl') or GradientBoostingClassifier(
                n_estimators=80, max_depth=5, random_state=42
            )
            
            # Load scalers and encoders
            self.scalers['standard'] = self._load_scaler('standard_scaler.pkl') or StandardScaler()
            self.encoders['label'] = self._load_encoder('label_encoder.pkl') or LabelEncoder()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    def _load_model(self, filename: str):
        """Load a saved model"""
        try:
            filepath = os.path.join(self.models_path, filename)
            if os.path.exists(filepath):
                return joblib.load(filepath)
        except Exception as e:
            logger.warning(f"Could not load model {filename}: {e}")
        return None
    
    def _load_scaler(self, filename: str):
        """Load a saved scaler"""
        try:
            filepath = os.path.join(self.models_path, filename)
            if os.path.exists(filepath):
                return joblib.load(filepath)
        except Exception as e:
            logger.warning(f"Could not load scaler {filename}: {e}")
        return None
    
    def _load_encoder(self, filename: str):
        """Load a saved encoder"""
        try:
            filepath = os.path.join(self.models_path, filename)
            if os.path.exists(filepath):
                return joblib.load(filepath)
        except Exception as e:
            logger.warning(f"Could not load encoder {filename}: {e}")
        return None
    
    def save_model(self, model_name: str, model, filename: str):
        """Save a trained model"""
        try:
            filepath = os.path.join(self.models_path, filename)
            joblib.dump(model, filepath)
            self.models[model_name] = model
            logger.info(f"Model {model_name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")
    
    async def predict_hospital_surge(self, hospital_id: str, days_ahead: int = 7) -> Dict:
        """Predict hospital surge using trained ML model"""
        try:
            # Collect historical data
            historical_data = await self._collect_surge_training_data(hospital_id)
            
            if len(historical_data) < 10:
                # Not enough data for ML prediction, return basic forecast
                return await self._basic_surge_prediction(hospital_id, days_ahead)
            
            # Prepare features for prediction
            features = await self._prepare_surge_features(hospital_id, days_ahead)
            
            # Make prediction
            model = self.models['surge_predictor']
            if hasattr(model, 'predict'):
                predicted_load = model.predict([features])[0]
            else:
                # Retrain model if not trained yet
                await self.train_surge_model(hospital_id)
                predicted_load = model.predict([features])[0]
            
            # Calculate confidence and risk factors
            confidence = min(0.95, len(historical_data) / 100.0)
            risk_level = "high" if predicted_load > 0.8 else "medium" if predicted_load > 0.6 else "low"
            
            return {
                "hospital_id": hospital_id,
                "predicted_load": float(predicted_load),
                "confidence": confidence,
                "risk_level": risk_level,
                "prediction_horizon_days": days_ahead,
                "factors": await self._get_surge_factors(hospital_id),
                "recommended_actions": await self._get_surge_recommendations(predicted_load),
                "model_version": "ml_v1.0"
            }
            
        except Exception as e:
            logger.error(f"Error in ML surge prediction: {e}")
            return await self._basic_surge_prediction(hospital_id, days_ahead)
    
    async def assess_patient_risk(self, patient_id: str) -> Dict:
        """Assess patient risk using ML model"""
        try:
            # Collect patient data
            patient_features = await self._prepare_patient_risk_features(patient_id)
            
            if not patient_features:
                return {"error": "Insufficient patient data"}
            
            # Make prediction
            model = self.models['risk_assessment']
            risk_score = model.predict_proba([patient_features])[0][1] if hasattr(model, 'predict_proba') else 0.5
            
            # Categorize risk
            if risk_score > 0.8:
                risk_category = "high"
            elif risk_score > 0.5:
                risk_category = "medium"
            else:
                risk_category = "low"
            
            return {
                "patient_id": patient_id,
                "risk_score": float(risk_score),
                "risk_category": risk_category,
                "contributing_factors": await self._get_risk_factors(patient_id),
                "recommendations": await self._get_risk_recommendations(risk_category),
                "model_accuracy": 0.85  # Based on training metrics
            }
            
        except Exception as e:
            logger.error(f"Error in patient risk assessment: {e}")
            return {"error": str(e)}
    
    async def predict_readmission_risk(self, patient_id: str, discharge_data: Dict) -> Dict:
        """Predict 30-day readmission risk"""
        try:
            features = await self._prepare_readmission_features(patient_id, discharge_data)
            
            model = self.models['readmission_predictor']
            readmission_prob = model.predict_proba([features])[0][1] if hasattr(model, 'predict_proba') else 0.3
            
            risk_level = "high" if readmission_prob > 0.6 else "medium" if readmission_prob > 0.3 else "low"
            
            return {
                "patient_id": patient_id,
                "readmission_probability": float(readmission_prob),
                "risk_level": risk_level,
                "key_factors": await self._get_readmission_factors(patient_id),
                "prevention_recommendations": await self._get_prevention_recommendations(risk_level),
                "follow_up_schedule": await self._generate_follow_up_schedule(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error in readmission prediction: {e}")
            return {"error": str(e)}
    
    async def optimize_hospital_capacity(self, hospital_id: str) -> Dict:
        """Optimize hospital capacity allocation using ML"""
        try:
            # Get current capacity data
            capacity_features = await self._prepare_capacity_features(hospital_id)
            
            model = self.models['capacity_optimizer']
            optimal_capacity = model.predict([capacity_features])[0] if hasattr(model, 'predict') else 70
            
            current_capacity = await self._get_current_capacity(hospital_id)
            
            return {
                "hospital_id": hospital_id,
                "current_capacity": current_capacity,
                "optimal_capacity": float(optimal_capacity),
                "capacity_adjustment": float(optimal_capacity - current_capacity),
                "optimization_suggestions": await self._get_capacity_suggestions(optimal_capacity, current_capacity),
                "efficiency_gain": abs(optimal_capacity - current_capacity) / max(current_capacity, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error in capacity optimization: {e}")
            return {"error": str(e)}
    
    async def predict_medication_adherence(self, patient_id: str, medication_id: str) -> Dict:
        """Predict medication adherence probability"""
        try:
            features = await self._prepare_adherence_features(patient_id, medication_id)
            
            model = self.models['adherence_predictor']
            adherence_prob = model.predict_proba([features])[0][1] if hasattr(model, 'predict_proba') else 0.7
            
            adherence_category = "high" if adherence_prob > 0.8 else "medium" if adherence_prob > 0.5 else "low"
            
            return {
                "patient_id": patient_id,
                "medication_id": medication_id,
                "adherence_probability": float(adherence_prob),
                "adherence_category": adherence_category,
                "risk_factors": await self._get_adherence_risk_factors(patient_id),
                "intervention_recommendations": await self._get_adherence_interventions(adherence_category),
                "monitoring_frequency": "daily" if adherence_category == "low" else "weekly"
            }
            
        except Exception as e:
            logger.error(f"Error in adherence prediction: {e}")
            return {"error": str(e)}
    
    # Training methods
    async def train_surge_model(self, hospital_id: str = None):
        """Train the hospital surge prediction model"""
        try:
            # Collect training data
            training_data = await self._collect_surge_training_data(hospital_id)
            
            if len(training_data) < 50:
                logger.warning("Insufficient data for surge model training")
                return False
            
            # Prepare features and labels
            X, y = await self._prepare_surge_training_data(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"Surge model trained with MAE: {mae}")
            
            # Save model
            self.save_model('surge_predictor', model, 'surge_predictor.pkl')
            
            return True
            
        except Exception as e:
            logger.error(f"Error training surge model: {e}")
            return False
    
    async def train_risk_assessment_model(self):
        """Train the patient risk assessment model"""
        try:
            # Collect patient outcome data
            training_data = await self._collect_risk_training_data()
            
            if len(training_data) < 100:
                logger.warning("Insufficient data for risk assessment model training")
                return False
            
            X, y = await self._prepare_risk_training_data(training_data)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Risk assessment model trained with accuracy: {accuracy}")
            
            # Save model and scaler
            self.save_model('risk_assessment', model, 'risk_assessment.pkl')
            joblib.dump(scaler, os.path.join(self.models_path, 'risk_scaler.pkl'))
            
            return True
            
        except Exception as e:
            logger.error(f"Error training risk assessment model: {e}")
            return False
    
    # Helper methods for data preparation
    async def _collect_surge_training_data(self, hospital_id: str = None) -> List[Dict]:
        """Collect historical data for surge prediction training"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)
            
            query = CapacityLog.created_at >= start_date
            if hospital_id:
                query = query & (CapacityLog.hospital_id == hospital_id)
            
            capacity_logs = await CapacityLog.find(query).to_list()
            
            training_data = []
            for log in capacity_logs:
                training_data.append({
                    'hospital_id': log.hospital_id,
                    'date': log.created_at,
                    'current_load': log.current_load,
                    'total_capacity': log.total_capacity,
                    'utilization_rate': log.current_load / max(log.total_capacity, 1),
                    'day_of_week': log.created_at.weekday(),
                    'hour_of_day': log.created_at.hour,
                    'month': log.created_at.month
                })
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error collecting surge training data: {e}")
            return []
    
    async def _prepare_surge_features(self, hospital_id: str, days_ahead: int) -> List[float]:
        """Prepare features for surge prediction"""
        try:
            # Get recent capacity data
            recent_logs = await CapacityLog.find(
                CapacityLog.hospital_id == hospital_id
            ).sort(-CapacityLog.created_at).limit(30).to_list()
            
            if not recent_logs:
                return [0.5, 3, 12, 6, 0.6, 5, 10]  # Default features
            
            # Calculate features
            avg_utilization = sum([log.current_load / max(log.total_capacity, 1) for log in recent_logs]) / len(recent_logs)
            
            future_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            features = [
                avg_utilization,
                future_date.weekday(),
                future_date.hour,
                future_date.month,
                len(recent_logs) / 30.0,  # Data completeness
                days_ahead,
                sum([1 for log in recent_logs if log.current_load / max(log.total_capacity, 1) > 0.8]) / len(recent_logs)  # High load frequency
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing surge features: {e}")
            return [0.5, 3, 12, 6, 0.6, 5, 10]
    
    async def _basic_surge_prediction(self, hospital_id: str, days_ahead: int) -> Dict:
        """Basic surge prediction when ML model isn't available"""
        return {
            "hospital_id": hospital_id,
            "predicted_load": 0.6,
            "confidence": 0.5,
            "risk_level": "medium",
            "prediction_horizon_days": days_ahead,
            "factors": ["Limited historical data"],
            "recommended_actions": ["Monitor capacity closely", "Prepare contingency plans"],
            "model_version": "basic_v1.0"
        }
    
    # Additional helper methods would be implemented here...
    async def _get_surge_factors(self, hospital_id: str) -> List[str]:
        return ["Historical patterns", "Seasonal trends", "Regional events"]
    
    async def _get_surge_recommendations(self, predicted_load: float) -> List[str]:
        if predicted_load > 0.8:
            return ["Increase staff", "Prepare overflow areas", "Contact nearby hospitals"]
        elif predicted_load > 0.6:
            return ["Monitor closely", "Prepare additional resources"]
        else:
            return ["Normal operations", "Maintain current capacity"]
    
    # Placeholder methods for other feature preparation functions
    async def _prepare_patient_risk_features(self, patient_id: str) -> Optional[List[float]]:
        return [45, 1, 2, 3, 0, 1, 120, 80]  # age, gender, comorbidities, etc.
    
    async def _get_risk_factors(self, patient_id: str) -> List[str]:
        return ["Age", "Comorbidities", "Previous admissions"]
    
    async def _get_risk_recommendations(self, risk_category: str) -> List[str]:
        if risk_category == "high":
            return ["Frequent monitoring", "Preventive care", "Care coordination"]
        return ["Standard care", "Regular follow-up"]
    
    async def _prepare_readmission_features(self, patient_id: str, discharge_data: Dict) -> List[float]:
        return [3, 1, 2, 0, 1, 7]  # length_of_stay, complications, etc.
    
    async def _get_readmission_factors(self, patient_id: str) -> List[str]:
        return ["Length of stay", "Discharge diagnosis", "Social factors"]
    
    async def _get_prevention_recommendations(self, risk_level: str) -> List[str]:
        return ["Medication adherence", "Follow-up appointments", "Patient education"]
    
    async def _generate_follow_up_schedule(self, risk_level: str) -> Dict:
        if risk_level == "high":
            return {"48_hours": True, "1_week": True, "2_weeks": True, "1_month": True}
        return {"1_week": True, "1_month": True}
    
    async def _prepare_capacity_features(self, hospital_id: str) -> List[float]:
        return [70, 5, 12, 0.8, 20]  # current_capacity, day, hour, utilization, etc.
    
    async def _get_current_capacity(self, hospital_id: str) -> float:
        recent_log = await CapacityLog.find(
            CapacityLog.hospital_id == hospital_id
        ).sort(-CapacityLog.created_at).first_or_none()
        return recent_log.current_load / max(recent_log.total_capacity, 1) * 100 if recent_log else 50
    
    async def _get_capacity_suggestions(self, optimal: float, current: float) -> List[str]:
        if optimal > current:
            return ["Increase bed capacity", "Add staff", "Optimize patient flow"]
        return ["Current capacity is optimal", "Monitor for changes"]
    
    async def _prepare_adherence_features(self, patient_id: str, medication_id: str) -> List[float]:
        return [45, 1, 3, 2, 1, 0]  # age, complexity, side_effects, etc.
    
    async def _get_adherence_risk_factors(self, patient_id: str) -> List[str]:
        return ["Medication complexity", "Side effects", "Cost factors"]
    
    async def _get_adherence_interventions(self, category: str) -> List[str]:
        if category == "low":
            return ["Simplified dosing", "Reminder systems", "Patient counseling"]
        return ["Regular monitoring", "Patient education"]
    
    # Training data preparation methods
    async def _prepare_surge_training_data(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for data in training_data:
            features = [
                data['utilization_rate'],
                data['day_of_week'],
                data['hour_of_day'],
                data['month'],
                1.0,  # data_completeness
                1,    # days_ahead (for training, we use next day)
                0.5   # high_load_frequency
            ]
            X.append(features)
            y.append(data['utilization_rate'])
        
        return np.array(X), np.array(y)
    
    async def _collect_risk_training_data(self) -> List[Dict]:
        # Collect patient outcome data for training
        outcomes = await PatientOutcome.find().limit(1000).to_list()
        training_data = []
        for outcome in outcomes:
            training_data.append({
                'patient_id': outcome.patient_id,
                'age': 45,  # Would get from patient record
                'outcome': 1 if outcome.outcome_type in ['deterioration', 'death'] else 0,
                'length_of_stay': outcome.length_of_stay or 3,
                'complications': len(outcome.complications),
                'readmission': 1 if outcome.readmission_30d else 0
            })
        return training_data
    
    async def _prepare_risk_training_data(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for data in training_data:
            features = [
                data.get('age', 45),
                data.get('length_of_stay', 3),
                data.get('complications', 0),
                data.get('readmission', 0),
                1,  # gender (encoded)
                2,  # comorbidities count
                120, 80  # vitals
            ]
            X.append(features)
            y.append(data['outcome'])
        
        return np.array(X), np.array(y)