from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    API_CALL = "api_call"
    DATA_CHANGE = "data_change"

class NodeType(str, Enum):
    TRIGGER = "trigger"
    HTTP_REQUEST = "http_request"
    DATABASE = "database"
    EMAIL = "email"
    SMS = "sms"
    NOTIFICATION = "notification"
    AI_ANALYSIS = "ai_analysis"
    CONDITION = "condition"
    TRANSFORM = "transform"
    DELAY = "delay"

class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    name: str
    parameters: dict = {}
    position: dict = {"x": 0, "y": 0}
    connections: List[str] = []  # Connected node IDs

class WorkflowTrigger(BaseModel):
    type: TriggerType
    schedule: Optional[str] = None  # Cron expression for scheduled workflows
    event_type: Optional[str] = None  # Event that triggers workflow
    conditions: dict = {}

class N8NWorkflow(Document):
    workflow_id: str = Field(..., unique=True, index=True)
    name: str
    description: Optional[str] = None
    
    # Workflow Definition
    nodes: List[WorkflowNode] = []
    connections: dict = {}  # Node connections mapping
    trigger: WorkflowTrigger
    
    # Status and Control
    status: WorkflowStatus = WorkflowStatus.DRAFT
    is_active: bool = False
    
    # Metadata
    category: str = "healthcare"  # "healthcare", "admin", "patient_care", "analytics"
    tags: List[str] = []
    
    # Execution Settings
    timeout_minutes: int = 30
    retry_attempts: int = 3
    error_handling: str = "stop"  # "stop", "continue", "retry"
    
    # Permissions
    created_by: str = Field(..., index=True)
    hospital_id: Optional[str] = Field(None, index=True)
    allowed_roles: List[str] = ["admin", "hospital"]
    
    # Statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    last_execution: Optional[datetime] = None
    average_execution_time: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "n8n_workflows"
        indexes = [
            "workflow_id",
            "status",
            "category",
            "created_by",
            "hospital_id",
            [("status", 1), ("category", 1)],
            [("hospital_id", 1), ("status", 1)]
        ]

class WorkflowExecution(Document):
    execution_id: str = Field(..., unique=True, index=True)
    workflow_id: str = Field(..., index=True)
    workflow_name: str
    
    # Execution Details
    status: str = "running"  # "running", "success", "failed", "cancelled"
    trigger_data: dict = {}
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Execution Flow
    current_node: Optional[str] = None
    completed_nodes: List[str] = []
    failed_nodes: List[str] = []
    
    # Data Flow
    input_data: dict = {}
    output_data: dict = {}
    node_outputs: dict = {}  # {node_id: output_data}
    
    # Error Handling
    error_message: Optional[str] = None
    error_node: Optional[str] = None
    retry_count: int = 0
    
    # Logs
    execution_logs: List[dict] = []
    
    # Context
    triggered_by: str  # User ID or system
    execution_context: dict = {}  # Additional context data
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "workflow_executions"
        indexes = [
            "execution_id",
            "workflow_id",
            "status",
            "started_at",
            "triggered_by",
            [("workflow_id", 1), ("started_at", -1)],
            [("status", 1), ("started_at", -1)]
        ]

class WorkflowTemplate(Document):
    template_id: str = Field(..., unique=True, index=True)
    name: str
    description: str
    category: str
    
    # Template Definition
    template_data: dict = {}  # Complete workflow structure
    parameters: List[dict] = []  # Required parameters for template
    
    # Usage
    use_count: int = 0
    rating: float = 0.0
    reviews: List[dict] = []
    
    # Metadata
    author: str
    version: str = "1.0"
    tags: List[str] = []
    is_public: bool = True
    
    # Requirements
    required_integrations: List[str] = []
    complexity_level: str = "beginner"  # "beginner", "intermediate", "advanced"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "workflow_templates"
        indexes = [
            "template_id",
            "category",
            "author",
            "is_public",
            [("category", 1), ("rating", -1)]
        ]

class AutomationRule(Document):
    rule_id: str = Field(..., unique=True, index=True)
    name: str
    description: str
    
    # Rule Configuration
    trigger_conditions: dict = {}  # Conditions that activate the rule
    actions: List[dict] = []  # Actions to execute when triggered
    
    # Scope
    hospital_id: Optional[str] = Field(None, index=True)
    department: Optional[str] = None
    applies_to: str = "all"  # "all", "patients", "staff", "specific"
    target_ids: List[str] = []  # Specific IDs if applies_to is "specific"
    
    # Status
    is_active: bool = True
    priority: int = 1  # 1 (low) to 5 (high)
    
    # Execution Limits
    max_executions_per_hour: Optional[int] = None
    max_executions_per_day: Optional[int] = None
    cooldown_minutes: int = 0
    
    # Tracking
    total_triggers: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    last_triggered: Optional[datetime] = None
    
    # Configuration
    created_by: str = Field(..., index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "automation_rules"
        indexes = [
            "rule_id",
            "hospital_id",
            "is_active",
            "created_by",
            [("hospital_id", 1), ("is_active", 1)],
            [("is_active", 1), ("priority", -1)]
        ]

# Pre-built Healthcare Workflow Templates
HEALTHCARE_WORKFLOW_TEMPLATES = {
    "patient_admission_workflow": {
        "name": "Patient Admission Automation",
        "description": "Automate patient admission process with notifications and resource allocation",
        "nodes": [
            {
                "id": "trigger_admission",
                "type": "event",
                "name": "Patient Admission Trigger",
                "parameters": {"event_type": "patient_admitted"}
            },
            {
                "id": "notify_staff",
                "type": "notification",
                "name": "Notify Medical Staff",
                "parameters": {"roles": ["nurse", "doctor"], "message": "New patient admission"}
            },
            {
                "id": "allocate_bed",
                "type": "database",
                "name": "Allocate Hospital Bed",
                "parameters": {"action": "update_capacity"}
            },
            {
                "id": "create_medical_record",
                "type": "database",
                "name": "Create Medical Record",
                "parameters": {"collection": "medical_records"}
            }
        ]
    },
    
    "medication_reminder_workflow": {
        "name": "Automated Medication Reminders",
        "description": "Send automated medication reminders to patients",
        "nodes": [
            {
                "id": "schedule_trigger",
                "type": "schedule",
                "name": "Daily Medication Check",
                "parameters": {"cron": "0 */2 * * *"}  # Every 2 hours
            },
            {
                "id": "check_due_medications",
                "type": "database",
                "name": "Find Due Medications",
                "parameters": {"query": "due_medications"}
            },
            {
                "id": "send_reminder",
                "type": "notification",
                "name": "Send Medication Reminder",
                "parameters": {"type": "medication_reminder"}
            },
            {
                "id": "log_reminder",
                "type": "database",
                "name": "Log Reminder Sent",
                "parameters": {"action": "create_log"}
            }
        ]
    },
    
    "emergency_response_workflow": {
        "name": "Emergency Response Automation",
        "description": "Automated emergency response system",
        "nodes": [
            {
                "id": "emergency_trigger",
                "type": "event",
                "name": "Emergency Alert Trigger",
                "parameters": {"event_type": "emergency_alert"}
            },
            {
                "id": "assess_severity",
                "type": "condition",
                "name": "Assess Emergency Severity",
                "parameters": {"conditions": [{"field": "severity", "operator": ">=", "value": "high"}]}
            },
            {
                "id": "notify_emergency_team",
                "type": "notification",
                "name": "Alert Emergency Team",
                "parameters": {"urgent": True, "roles": ["emergency_team"]}
            },
            {
                "id": "contact_emergency_services",
                "type": "http_request",
                "name": "Contact Emergency Services",
                "parameters": {"method": "POST", "url": "/emergency/dispatch"}
            },
            {
                "id": "update_patient_status",
                "type": "database",
                "name": "Update Patient Status",
                "parameters": {"status": "emergency_care"}
            }
        ]
    },
    
    "discharge_planning_workflow": {
        "name": "Patient Discharge Planning",
        "description": "Automate patient discharge process and follow-up care",
        "nodes": [
            {
                "id": "discharge_trigger",
                "type": "event",
                "name": "Discharge Order Trigger",
                "parameters": {"event_type": "discharge_ordered"}
            },
            {
                "id": "generate_discharge_summary",
                "type": "ai_analysis",
                "name": "Generate Discharge Summary",
                "parameters": {"ai_model": "discharge_summary_generator"}
            },
            {
                "id": "schedule_follow_up",
                "type": "database",
                "name": "Schedule Follow-up Appointment",
                "parameters": {"action": "create_appointment", "days_ahead": 7}
            },
            {
                "id": "send_discharge_instructions",
                "type": "notification",
                "name": "Send Discharge Instructions",
                "parameters": {"type": "discharge_instructions"}
            },
            {
                "id": "update_bed_availability",
                "type": "database",
                "name": "Update Bed Availability",
                "parameters": {"action": "release_bed"}
            }
        ]
    },
    
    "capacity_optimization_workflow": {
        "name": "Hospital Capacity Optimization",
        "description": "Automatically optimize hospital capacity based on demand predictions",
        "nodes": [
            {
                "id": "capacity_check_trigger",
                "type": "schedule",
                "name": "Hourly Capacity Check",
                "parameters": {"cron": "0 * * * *"}  # Every hour
            },
            {
                "id": "analyze_current_capacity",
                "type": "ai_analysis",
                "name": "Analyze Current Capacity",
                "parameters": {"ai_model": "capacity_analyzer"}
            },
            {
                "id": "predict_demand",
                "type": "ai_analysis",
                "name": "Predict Patient Demand",
                "parameters": {"ai_model": "surge_predictor"}
            },
            {
                "id": "optimize_allocation",
                "type": "condition",
                "name": "Check if Optimization Needed",
                "parameters": {"conditions": [{"field": "predicted_load", "operator": ">", "value": 0.8}]}
            },
            {
                "id": "notify_management",
                "type": "notification",
                "name": "Notify Hospital Management",
                "parameters": {"type": "capacity_alert", "roles": ["admin", "manager"]}
            },
            {
                "id": "auto_adjust_resources",
                "type": "database",
                "name": "Auto-adjust Resources",
                "parameters": {"action": "optimize_capacity"}
            }
        ]
    },
    
    "patient_risk_assessment_workflow": {
        "name": "Automated Patient Risk Assessment",
        "description": "Continuously assess patient risk and trigger interventions",
        "nodes": [
            {
                "id": "vital_signs_trigger",
                "type": "event",
                "name": "Vital Signs Update Trigger",
                "parameters": {"event_type": "vital_signs_updated"}
            },
            {
                "id": "risk_analysis",
                "type": "ai_analysis",
                "name": "AI Risk Assessment",
                "parameters": {"ai_model": "patient_risk_assessor"}
            },
            {
                "id": "high_risk_check",
                "type": "condition",
                "name": "Check High Risk Status",
                "parameters": {"conditions": [{"field": "risk_score", "operator": ">", "value": 0.8}]}
            },
            {
                "id": "alert_medical_team",
                "type": "notification",
                "name": "Alert Medical Team",
                "parameters": {"urgent": True, "type": "high_risk_patient"}
            },
            {
                "id": "update_care_plan",
                "type": "database",
                "name": "Update Care Plan",
                "parameters": {"action": "escalate_care_plan"}
            },
            {
                "id": "schedule_monitoring",
                "type": "database",
                "name": "Increase Monitoring Frequency",
                "parameters": {"monitoring_interval": "15_minutes"}
            }
        ]
    },
    
    "appointment_optimization_workflow": {
        "name": "Appointment Scheduling Optimization",
        "description": "Optimize appointment scheduling based on demand and resources",
        "nodes": [
            {
                "id": "appointment_request_trigger",
                "type": "event",
                "name": "Appointment Request Trigger",
                "parameters": {"event_type": "appointment_requested"}
            },
            {
                "id": "analyze_availability",
                "type": "ai_analysis",
                "name": "Analyze Doctor Availability",
                "parameters": {"ai_model": "availability_optimizer"}
            },
            {
                "id": "optimize_scheduling",
                "type": "ai_analysis",
                "name": "Optimize Appointment Time",
                "parameters": {"ai_model": "schedule_optimizer"}
            },
            {
                "id": "confirm_appointment",
                "type": "database",
                "name": "Confirm Appointment",
                "parameters": {"action": "create_appointment"}
            },
            {
                "id": "send_confirmation",
                "type": "notification",
                "name": "Send Appointment Confirmation",
                "parameters": {"type": "appointment_confirmation"}
            },
            {
                "id": "add_calendar_event",
                "type": "http_request",
                "name": "Add to Calendar",
                "parameters": {"method": "POST", "url": "/calendar/events"}
            }
        ]
    }
}