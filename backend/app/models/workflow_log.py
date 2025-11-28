from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """n8n workflow execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


class WorkflowLog(Document):
    """n8n workflow execution log model"""
    workflow_name: str = Field(index=True)
    execution_id: str
    status: WorkflowStatus = WorkflowStatus.RUNNING
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        name = "n8n_workflow_logs"
        indexes = [
            "workflow_name",
            "status",
            "created_at",
            [("workflow_name", 1), ("created_at", -1)]
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_name": "hospital-data-sync",
                "execution_id": "exec_123456",
                "status": "success"
            }
        }
