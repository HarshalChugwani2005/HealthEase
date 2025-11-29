from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.analytics import Analytics, HealthAlert, PatientOutcome, AnalyticsType
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.referral import Referral
from app.models.appointment import Appointment
from app.middleware.auth import get_current_user, require_role
from app.models.user import User
from app.services.ai_service import AIService
import uuid

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(
    period_days: int = Query(30, description="Analysis period in days"),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard analytics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        analytics_data = {}
        
        if current_user.role == "hospital":
            hospital_id = current_user.hospital_id or current_user.id
            
            # Hospital-specific analytics
            analytics_data = {
                "hospital_performance": await get_hospital_performance(hospital_id, start_date, end_date),
                "patient_flow": await get_patient_flow_analytics(hospital_id, start_date, end_date),
                "capacity_utilization": await get_capacity_analytics(hospital_id, start_date, end_date),
                "revenue_analytics": await get_revenue_analytics(hospital_id, start_date, end_date)
            }
            
        elif current_user.role == "admin":
            # System-wide analytics
            analytics_data = {
                "system_overview": await get_system_overview(start_date, end_date),
                "hospital_comparison": await get_hospital_comparison(start_date, end_date),
                "population_health": await get_population_health_analytics(start_date, end_date),
                "financial_summary": await get_financial_summary(start_date, end_date)
            }
            
        elif current_user.role == "patient":
            # Patient personal analytics
            analytics_data = {
                "health_trends": await get_patient_health_trends(current_user.id, start_date, end_date),
                "appointment_history": await get_patient_appointment_analytics(current_user.id, start_date, end_date),
                "medication_adherence": await get_medication_adherence_analytics(current_user.id, start_date, end_date)
            }
            
        return {
            "period": {"start": start_date, "end": end_date, "days": period_days},
            "analytics": analytics_data,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictive")
async def get_predictive_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered predictive insights"""
    try:
        ai_service = AIService()
        
        if current_user.role == "hospital":
            hospital_id = current_user.hospital_id or current_user.id
            
            # Hospital predictive analytics
            insights = await ai_service.generate_hospital_predictions(hospital_id)
            
        elif current_user.role == "admin":
            # System-wide predictions
            insights = await ai_service.generate_system_predictions()
            
        else:
            raise HTTPException(status_code=403, detail="Access denied")
            
        return {"predictive_insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-alerts")
async def get_health_alerts(
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """Get health alerts"""
    try:
        query = {}
        
        if active_only:
            query["status"] = "active"
        if severity:
            query["severity"] = severity
        if alert_type:
            query["alert_type"] = alert_type
            
        # Filter based on user role
        if current_user.role == "hospital":
            hospital_id = current_user.hospital_id or current_user.id
            # Get alerts relevant to this hospital
            alerts = await HealthAlert.find(
                HealthAlert.target_ids.in_([hospital_id]) | 
                (HealthAlert.target_type == "global")
            ).sort(-HealthAlert.issued_at).to_list()
        elif current_user.role == "patient":
            # Get alerts relevant to this patient
            alerts = await HealthAlert.find(
                HealthAlert.target_ids.in_([current_user.id]) | 
                (HealthAlert.target_type.in_(["global", "regional"]))
            ).sort(-HealthAlert.issued_at).to_list()
        else:
            # Admin sees all alerts
            alerts = await HealthAlert.find().sort(-HealthAlert.issued_at).to_list()
            
        return {"alerts": alerts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health-alerts", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def create_health_alert(
    alert_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new health alert"""
    try:
        alert = HealthAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            title=alert_data["title"],
            message=alert_data["message"],
            target_type=alert_data["target_type"],
            target_ids=alert_data.get("target_ids", []),
            region=alert_data.get("region"),
            city=alert_data.get("city"),
            coordinates=alert_data.get("coordinates"),
            radius_km=alert_data.get("radius_km"),
            recommended_actions=alert_data.get("recommended_actions", []),
            emergency_contacts=alert_data.get("emergency_contacts", []),
            expires_at=alert_data.get("expires_at")
        )
        
        await alert.create()
        
        # TODO: Implement alert broadcasting to affected users
        
        return {"alert": alert, "message": "Health alert created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient-outcomes")
async def get_patient_outcomes(
    hospital_id: Optional[str] = Query(None),
    outcome_type: Optional[str] = Query(None),
    days: int = Query(90),
    current_user: User = Depends(get_current_user)
):
    """Get patient outcome analytics"""
    try:
        if current_user.role not in ["hospital", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
            
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = PatientOutcome.admission_date >= start_date
        
        if hospital_id and current_user.role == "admin":
            query = query & (PatientOutcome.hospital_id == hospital_id)
        elif current_user.role == "hospital":
            query = query & (PatientOutcome.hospital_id == (current_user.hospital_id or current_user.id))
            
        if outcome_type:
            query = query & (PatientOutcome.outcome_type == outcome_type)
            
        outcomes = await PatientOutcome.find(query).sort(-PatientOutcome.admission_date).to_list()
        
        # Calculate summary statistics
        total_outcomes = len(outcomes)
        readmission_30d = len([o for o in outcomes if o.readmission_30d])
        avg_satisfaction = sum([o.satisfaction_score for o in outcomes if o.satisfaction_score]) / max(1, len([o for o in outcomes if o.satisfaction_score]))
        
        outcome_distribution = {}
        for outcome in outcomes:
            outcome_distribution[outcome.outcome_type] = outcome_distribution.get(outcome.outcome_type, 0) + 1
            
        return {
            "summary": {
                "total_outcomes": total_outcomes,
                "readmission_rate_30d": (readmission_30d / max(1, total_outcomes)) * 100,
                "average_satisfaction": round(avg_satisfaction, 2),
                "outcome_distribution": outcome_distribution
            },
            "outcomes": outcomes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient-outcomes", dependencies=[Depends(require_role(["hospital"]))])
async def create_patient_outcome(
    outcome_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Record patient outcome"""
    try:
        outcome = PatientOutcome(
            patient_id=outcome_data["patient_id"],
            hospital_id=current_user.hospital_id or current_user.id,
            visit_id=outcome_data.get("visit_id"),
            admission_date=datetime.fromisoformat(outcome_data["admission_date"]),
            discharge_date=datetime.fromisoformat(outcome_data["discharge_date"]) if outcome_data.get("discharge_date") else None,
            primary_diagnosis=outcome_data["primary_diagnosis"],
            secondary_diagnoses=outcome_data.get("secondary_diagnoses", []),
            procedures=outcome_data.get("procedures", []),
            medications=outcome_data.get("medications", []),
            outcome_type=outcome_data["outcome_type"],
            satisfaction_score=outcome_data.get("satisfaction_score"),
            complications=outcome_data.get("complications", []),
            total_cost=outcome_data.get("total_cost"),
            insurance_coverage=outcome_data.get("insurance_coverage"),
            care_quality_score=outcome_data.get("care_quality_score"),
            wait_times=outcome_data.get("wait_times", {}),
            follow_up_compliance=outcome_data.get("follow_up_compliance", False)
        )
        
        # Calculate length of stay
        if outcome.discharge_date:
            outcome.length_of_stay = (outcome.discharge_date - outcome.admission_date).days
            
        await outcome.create()
        
        return {"outcome": outcome, "message": "Patient outcome recorded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for analytics calculations
async def get_hospital_performance(hospital_id: str, start_date: datetime, end_date: datetime):
    """Calculate hospital performance metrics"""
    try:
        # Get referrals, appointments, outcomes for the hospital
        referrals = await Referral.find(
            Referral.hospital_id == hospital_id,
            Referral.created_at >= start_date,
            Referral.created_at <= end_date
        ).to_list()
        
        appointments = await Appointment.find(
            Appointment.hospital_id == hospital_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).to_list()
        
        outcomes = await PatientOutcome.find(
            PatientOutcome.hospital_id == hospital_id,
            PatientOutcome.admission_date >= start_date,
            PatientOutcome.admission_date <= end_date
        ).to_list()
        
        return {
            "total_referrals": len(referrals),
            "total_appointments": len(appointments),
            "completed_appointments": len([a for a in appointments if a.status == "completed"]),
            "total_admissions": len(outcomes),
            "average_satisfaction": sum([o.satisfaction_score for o in outcomes if o.satisfaction_score]) / max(1, len([o for o in outcomes if o.satisfaction_score])),
            "readmission_rate": (len([o for o in outcomes if o.readmission_30d]) / max(1, len(outcomes))) * 100
        }
        
    except Exception as e:
        return {}

async def get_patient_flow_analytics(hospital_id: str, start_date: datetime, end_date: datetime):
    """Calculate patient flow analytics"""
    # Implementation would include capacity logs, appointment patterns, etc.
    return {
        "daily_patient_count": [],
        "peak_hours": [],
        "average_wait_time": 0,
        "capacity_utilization": 0
    }

async def get_capacity_analytics(hospital_id: str, start_date: datetime, end_date: datetime):
    """Calculate capacity utilization analytics"""
    # Implementation would analyze capacity logs
    return {
        "average_utilization": 0,
        "peak_utilization": 0,
        "underutilized_periods": []
    }

async def get_revenue_analytics(hospital_id: str, start_date: datetime, end_date: datetime):
    """Calculate revenue analytics"""
    # Implementation would analyze referral payments, appointments, etc.
    return {
        "total_revenue": 0,
        "revenue_by_source": {},
        "revenue_trend": []
    }

async def get_system_overview(start_date: datetime, end_date: datetime):
    """Get system-wide overview"""
    hospitals = await Hospital.find().to_list()
    patients = await Patient.find().to_list()
    
    return {
        "total_hospitals": len(hospitals),
        "total_patients": len(patients),
        "active_hospitals": len([h for h in hospitals if h.is_active]),
        "system_uptime": "99.9%"  # This would be calculated from monitoring data
    }

async def get_hospital_comparison(start_date: datetime, end_date: datetime):
    """Compare hospital performances"""
    return {
        "top_performing_hospitals": [],
        "performance_metrics": []
    }

async def get_population_health_analytics(start_date: datetime, end_date: datetime):
    """Get population health insights"""
    return {
        "common_diagnoses": [],
        "health_trends": [],
        "risk_factors": []
    }

async def get_financial_summary(start_date: datetime, end_date: datetime):
    """Get financial summary"""
    return {
        "total_transactions": 0,
        "revenue_breakdown": {},
        "payment_trends": []
    }

async def get_patient_health_trends(patient_id: str, start_date: datetime, end_date: datetime):
    """Get patient health trends"""
    return {
        "appointments_count": 0,
        "medications_count": 0,
        "health_score_trend": []
    }

async def get_patient_appointment_analytics(patient_id: str, start_date: datetime, end_date: datetime):
    """Get patient appointment analytics"""
    appointments = await Appointment.find(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).to_list()
    
    return {
        "total_appointments": len(appointments),
        "completed_appointments": len([a for a in appointments if a.status == "completed"]),
        "cancelled_appointments": len([a for a in appointments if a.status == "cancelled"]),
        "appointment_types": {}
    }

async def get_medication_adherence_analytics(patient_id: str, start_date: datetime, end_date: datetime):
    """Get medication adherence analytics"""
    return {
        "adherence_percentage": 0,
        "missed_doses": 0,
        "medications_count": 0
    }