from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    BLOOD_PRESSURE_MONITOR = "blood_pressure_monitor"
    GLUCOSE_METER = "glucose_meter"
    HEART_RATE_MONITOR = "heart_rate_monitor"
    PULSE_OXIMETER = "pulse_oximeter"
    THERMOMETER = "thermometer"
    WEIGHT_SCALE = "weight_scale"
    FITNESS_TRACKER = "fitness_tracker"
    SLEEP_MONITOR = "sleep_monitor"
    ECG_MONITOR = "ecg_monitor"
    INHALER_SENSOR = "inhaler_sensor"

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class VitalSign(BaseModel):
    type: str  # "blood_pressure", "heart_rate", "temperature", etc.
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    normal_range: dict = {}  # {"min": 80, "max": 120}
    is_abnormal: bool = False
    notes: Optional[str] = None

class AlertRule(BaseModel):
    parameter: str  # "heart_rate", "blood_pressure_systolic"
    condition: str  # "greater_than", "less_than", "between"
    threshold_value: float
    threshold_max: Optional[float] = None
    alert_message: str
    severity: str  # "low", "medium", "high"

class IoTDevice(Document):
    device_id: str = Field(..., unique=True, index=True)
    patient_id: str = Field(..., index=True)
    hospital_id: Optional[str] = Field(None, index=True)
    
    # Device Information
    device_type: DeviceType
    brand: str
    model: str
    serial_number: str
    mac_address: Optional[str] = None
    
    # Device Status
    status: DeviceStatus = DeviceStatus.ACTIVE
    battery_level: Optional[int] = None  # 0-100%
    last_sync: Optional[datetime] = None
    firmware_version: Optional[str] = None
    
    # Configuration
    sync_interval: int = 300  # seconds
    alert_rules: List[AlertRule] = []
    data_retention_days: int = 90
    
    # Location
    location: Optional[str] = None
    coordinates: Optional[List[float]] = None  # [lat, lng]
    
    # Connectivity
    connection_type: str = "bluetooth"  # "bluetooth", "wifi", "cellular"
    last_ip_address: Optional[str] = None
    
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_maintenance: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "iot_devices"
        indexes = [
            "device_id",
            "patient_id",
            "hospital_id",
            "device_type",
            "status",
            [("patient_id", 1), ("status", 1)],
            [("device_type", 1), ("status", 1)]
        ]

class HealthData(Document):
    device_id: str = Field(..., index=True)
    patient_id: str = Field(..., index=True)
    
    # Data Collection
    vital_signs: List[VitalSign] = []
    raw_data: dict = {}  # Original device data
    processed_data: dict = {}  # Processed/calculated values
    
    # Timestamp
    recorded_at: datetime = Field(..., index=True)
    received_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Data Quality
    quality_score: float = 1.0  # 0.0 to 1.0
    anomalies_detected: List[str] = []
    validation_errors: List[str] = []
    
    # Context
    activity_context: Optional[str] = None  # "resting", "exercise", "sleep"
    medication_taken: bool = False
    notes: Optional[str] = None
    
    # Alerts Generated
    alerts_triggered: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "health_data"
        indexes = [
            "device_id",
            "patient_id",
            "recorded_at",
            [("patient_id", 1), ("recorded_at", -1)],
            [("device_id", 1), ("recorded_at", -1)]
        ]

class TelemedicineSession(Document):
    session_id: str = Field(..., unique=True, index=True)
    appointment_id: str = Field(..., index=True)
    patient_id: str = Field(..., index=True)
    doctor_id: str = Field(..., index=True)
    hospital_id: str = Field(..., index=True)
    
    # Session Details
    session_type: str = "video_consultation"  # "video", "audio_only", "chat"
    status: str = "scheduled"  # "scheduled", "active", "completed", "cancelled", "no_show"
    
    # Technical Details
    platform: str = "webrtc"  # "webrtc", "zoom", "teams"
    room_id: str
    session_url: str
    backup_url: Optional[str] = None
    
    # Timing
    scheduled_start: datetime = Field(..., index=True)
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    # Session Data
    recording_enabled: bool = False
    recording_url: Optional[str] = None
    screen_sharing_used: bool = False
    chat_logs: List[dict] = []
    
    # Clinical Data
    consultation_notes: Optional[str] = None
    prescriptions_issued: List[str] = []  # Prescription IDs
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    
    # Quality Metrics
    connection_quality: Optional[str] = None  # "excellent", "good", "fair", "poor"
    audio_quality: Optional[str] = None
    video_quality: Optional[str] = None
    patient_satisfaction: Optional[int] = None  # 1-5 rating
    
    # Technical Issues
    technical_issues: List[str] = []
    disconnections: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "telemedicine_sessions"
        indexes = [
            "session_id",
            "appointment_id",
            "patient_id",
            "doctor_id",
            "hospital_id",
            "scheduled_start",
            "status",
            [("doctor_id", 1), ("scheduled_start", 1)],
            [("patient_id", 1), ("scheduled_start", 1)]
        ]

class EmergencyAlert(Document):
    alert_id: str = Field(..., unique=True, index=True)
    patient_id: str = Field(..., index=True)
    device_id: Optional[str] = Field(None, index=True)
    
    # Alert Details
    alert_type: str = Field(..., index=True)  # "fall_detection", "heart_rate_critical", "no_movement"
    severity: str = Field(..., index=True)  # "low", "medium", "high", "critical"
    message: str
    
    # Location
    location: Optional[str] = None
    coordinates: Optional[List[float]] = None
    indoor_location: Optional[str] = None  # "bedroom", "kitchen", etc.
    
    # Status
    status: str = "active"  # "active", "acknowledged", "resolved", "false_alarm"
    triggered_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Response
    emergency_contacts_notified: List[str] = []
    responders_assigned: List[str] = []  # Emergency responder IDs
    estimated_arrival: Optional[datetime] = None
    
    # Medical Context
    vital_signs_at_trigger: dict = {}
    medical_history_relevant: List[str] = []
    current_medications: List[str] = []
    
    # Actions Taken
    actions_taken: List[str] = []
    response_time_minutes: Optional[int] = None
    outcome: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "emergency_alerts"
        indexes = [
            "alert_id",
            "patient_id",
            "device_id",
            "alert_type",
            "severity",
            "status",
            "triggered_at",
            [("patient_id", 1), ("triggered_at", -1)],
            [("status", 1), ("severity", 1)]
        ]