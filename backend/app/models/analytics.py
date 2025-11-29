from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AnalyticsType(str, Enum):
    PATIENT_FLOW = "patient_flow"
    HOSPITAL_PERFORMANCE = "hospital_performance"
    POPULATION_HEALTH = "population_health"
    PREDICTIVE_INSIGHTS = "predictive_insights"
    FINANCIAL_ANALYTICS = "financial_analytics"

class MetricType(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    TREND = "trend"
    PREDICTION = "prediction"

class DataPoint(BaseModel):
    timestamp: datetime
    value: float
    category: Optional[str] = None
    metadata: dict = {}

class HealthMetric(BaseModel):
    name: str
    value: float
    unit: str
    trend: str  # "increasing", "decreasing", "stable"
    change_percentage: Optional[float] = None
    benchmark: Optional[float] = None

class PredictiveInsight(BaseModel):
    type: str  # "admission_risk", "readmission_risk", "epidemic_outbreak"
    probability: float  # 0.0 to 1.0
    confidence_level: float  # 0.0 to 1.0
    factors: List[str] = []
    recommended_actions: List[str] = []
    time_horizon: str  # "24h", "7d", "30d"

class Analytics(Document):
    # Identification
    analytics_type: AnalyticsType = Field(..., index=True)
    hospital_id: Optional[str] = Field(None, index=True)
    patient_id: Optional[str] = Field(None, index=True)
    region: Optional[str] = Field(None, index=True)
    
    # Time Period
    period_start: datetime = Field(..., index=True)
    period_end: datetime = Field(..., index=True)
    
    # Data
    metrics: List[HealthMetric] = []
    data_points: List[DataPoint] = []
    predictive_insights: List[PredictiveInsight] = []
    
    # Summary
    title: str
    summary: str
    key_findings: List[str] = []
    alerts: List[str] = []
    
    # Metadata
    generated_by: str  # "ai_service", "scheduled_job", "user_request"
    data_sources: List[str] = []
    accuracy_score: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analytics"
        indexes = [
            "analytics_type",
            "hospital_id",
            "patient_id",
            "region",
            "period_start",
            "period_end",
            [("hospital_id", 1), ("analytics_type", 1)],
            [("period_start", 1), ("analytics_type", 1)]
        ]

class HealthAlert(Document):
    # Alert Details
    alert_type: str = Field(..., index=True)  # "outbreak", "capacity_warning", "medication_recall"
    severity: str = Field(..., index=True)  # "low", "medium", "high", "critical"
    title: str
    message: str
    
    # Targeting
    target_type: str  # "global", "regional", "hospital", "patient"
    target_ids: List[str] = []  # Hospital IDs, Patient IDs, etc.
    affected_count: int = 0
    
    # Geographic
    region: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[List[float]] = None  # [lat, lng]
    radius_km: Optional[float] = None
    
    # Status
    status: str = "active"  # active, resolved, expired
    issued_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Actions
    recommended_actions: List[str] = []
    emergency_contacts: List[str] = []
    external_links: List[str] = []
    
    # Tracking
    views: int = 0
    acknowledgments: int = 0
    shares: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "health_alerts"
        indexes = [
            "alert_type",
            "severity", 
            "status",
            "issued_at",
            "region",
            [("status", 1), ("severity", 1)],
            [("issued_at", 1), ("status", 1)]
        ]

class PatientOutcome(Document):
    patient_id: str = Field(..., index=True)
    hospital_id: str = Field(..., index=True)
    
    # Visit Details
    visit_id: Optional[str] = None
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    length_of_stay: Optional[int] = None  # days
    
    # Medical Details
    primary_diagnosis: str
    secondary_diagnoses: List[str] = []
    procedures: List[str] = []
    medications: List[str] = []
    
    # Outcome Metrics
    outcome_type: str  # "recovery", "improvement", "stable", "deterioration", "death"
    satisfaction_score: Optional[float] = None  # 1-10 scale
    readmission_30d: bool = False
    complications: List[str] = []
    
    # Cost Analysis
    total_cost: Optional[float] = None
    insurance_coverage: Optional[float] = None
    out_of_pocket: Optional[float] = None
    
    # Quality Indicators
    care_quality_score: Optional[float] = None
    wait_times: dict = {}  # {"registration": 15, "consultation": 30} in minutes
    follow_up_compliance: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "patient_outcomes"
        indexes = [
            "patient_id",
            "hospital_id",
            "admission_date",
            "outcome_type",
            "readmission_30d",
            [("hospital_id", 1), ("admission_date", 1)],
            [("patient_id", 1), ("admission_date", 1)]
        ]