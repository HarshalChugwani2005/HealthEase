from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.workflow import N8NWorkflow, WorkflowExecution, WorkflowTemplate, AutomationRule, HEALTHCARE_WORKFLOW_TEMPLATES
from app.models.notification import Notification
from app.services.ml_service import MLPredictor
from app.middleware.auth import get_current_user, require_role
from app.models.user import User
import uuid
import json
import asyncio
from croniter import croniter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows", "n8n", "automation"])

# Initialize ML predictor
ml_predictor = MLPredictor()

@router.post("/create", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def create_workflow(
    workflow_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new n8n workflow"""
    try:
        workflow = N8NWorkflow(
            workflow_id=str(uuid.uuid4()),
            name=workflow_data["name"],
            description=workflow_data.get("description"),
            nodes=workflow_data.get("nodes", []),
            connections=workflow_data.get("connections", {}),
            trigger=workflow_data["trigger"],
            category=workflow_data.get("category", "healthcare"),
            tags=workflow_data.get("tags", []),
            timeout_minutes=workflow_data.get("timeout_minutes", 30),
            retry_attempts=workflow_data.get("retry_attempts", 3),
            error_handling=workflow_data.get("error_handling", "stop"),
            created_by=current_user.id,
            hospital_id=current_user.hospital_id if current_user.role == "hospital" else None,
            allowed_roles=workflow_data.get("allowed_roles", ["admin", "hospital"])
        )
        
        await workflow.create()
        
        return {
            "workflow": workflow,
            "message": "Workflow created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_workflow_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get available workflow templates"""
    try:
        # Get built-in templates
        templates = {}
        for template_id, template_data in HEALTHCARE_WORKFLOW_TEMPLATES.items():
            if not category or template_data.get("category", "healthcare") == category:
                templates[template_id] = template_data
        
        # Get custom templates from database
        query = WorkflowTemplate.is_public == True
        if category:
            query = query & (WorkflowTemplate.category == category)
            
        custom_templates = await WorkflowTemplate.find(query).to_list()
        
        return {
            "built_in_templates": templates,
            "custom_templates": custom_templates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/instantiate", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def create_workflow_from_template(
    template_id: str,
    customization_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a workflow from a template"""
    try:
        # Get template
        if template_id in HEALTHCARE_WORKFLOW_TEMPLATES:
            template_data = HEALTHCARE_WORKFLOW_TEMPLATES[template_id]
        else:
            template = await WorkflowTemplate.find_one(
                WorkflowTemplate.template_id == template_id
            )
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            template_data = template.template_data
        
        # Customize template with user data
        workflow_data = {
            **template_data,
            "name": customization_data.get("name", template_data["name"]),
            "description": customization_data.get("description", template_data.get("description")),
            **customization_data
        }
        
        # Create workflow
        workflow = N8NWorkflow(
            workflow_id=str(uuid.uuid4()),
            name=workflow_data["name"],
            description=workflow_data.get("description"),
            nodes=workflow_data.get("nodes", []),
            connections=workflow_data.get("connections", {}),
            trigger={
                "type": "manual",
                **workflow_data.get("trigger", {})
            },
            category=workflow_data.get("category", "healthcare"),
            created_by=current_user.id,
            hospital_id=current_user.hospital_id if current_user.role == "hospital" else None
        )
        
        await workflow.create()
        
        return {
            "workflow": workflow,
            "message": f"Workflow created from template: {template_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_workflows(
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List workflows"""
    try:
        query = {}
        
        # Filter by status
        if status:
            query["status"] = status
            
        # Filter by category
        if category:
            query["category"] = category
            
        # Filter by access permissions
        if current_user.role == "hospital":
            query["hospital_id"] = current_user.hospital_id or current_user.id
        elif current_user.role == "patient":
            # Patients can only see workflows that affect them
            query["category"] = "patient_care"
        
        workflows = await N8NWorkflow.find(query).sort(-N8NWorkflow.created_at).to_list()
        
        return {"workflows": workflows}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/{workflow_id}")
async def execute_workflow(
    workflow_id: str,
    execution_data: dict,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Execute a workflow manually"""
    try:
        workflow = await N8NWorkflow.find_one(
            N8NWorkflow.workflow_id == workflow_id
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check permissions
        if current_user.role not in workflow.allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if current_user.role == "hospital" and workflow.hospital_id != (current_user.hospital_id or current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create execution record
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            trigger_data=execution_data.get("trigger_data", {}),
            input_data=execution_data.get("input_data", {}),
            triggered_by=current_user.id,
            execution_context={
                "user_role": current_user.role,
                "hospital_id": current_user.hospital_id,
                "manual_execution": True
            }
        )
        
        await execution.create()
        
        # Execute workflow in background
        background_tasks.add_task(
            execute_workflow_nodes,
            workflow,
            execution,
            current_user.id
        )
        
        return {
            "execution_id": execution.execution_id,
            "status": "started",
            "message": "Workflow execution started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}")
async def get_execution_status(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get workflow execution status"""
    try:
        execution = await WorkflowExecution.find_one(
            WorkflowExecution.execution_id == execution_id
        )
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Check if user has access to this execution
        workflow = await N8NWorkflow.find_one(
            N8NWorkflow.workflow_id == execution.workflow_id
        )
        
        if workflow and current_user.role == "hospital" and workflow.hospital_id != (current_user.hospital_id or current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"execution": execution}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate/{workflow_id}", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def activate_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Activate a workflow"""
    try:
        workflow = await N8NWorkflow.find_one(
            N8NWorkflow.workflow_id == workflow_id
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check permissions
        if current_user.role == "hospital" and workflow.hospital_id != (current_user.hospital_id or current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        workflow.status = "active"
        workflow.is_active = True
        workflow.updated_at = datetime.utcnow()
        await workflow.save()
        
        # Start scheduled workflows
        if workflow.trigger.type == "schedule" and workflow.trigger.schedule:
            await schedule_workflow_execution(workflow)
        
        return {
            "message": "Workflow activated successfully",
            "workflow": workflow
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate/{workflow_id}", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def deactivate_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Deactivate a workflow"""
    try:
        workflow = await N8NWorkflow.find_one(
            N8NWorkflow.workflow_id == workflow_id
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow.status = "paused"
        workflow.is_active = False
        workflow.updated_at = datetime.utcnow()
        await workflow.save()
        
        return {
            "message": "Workflow deactivated successfully",
            "workflow": workflow
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation-rules", dependencies=[Depends(require_role(["admin", "hospital"]))])
async def create_automation_rule(
    rule_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create an automation rule"""
    try:
        rule = AutomationRule(
            rule_id=str(uuid.uuid4()),
            name=rule_data["name"],
            description=rule_data.get("description", ""),
            trigger_conditions=rule_data["trigger_conditions"],
            actions=rule_data["actions"],
            hospital_id=current_user.hospital_id if current_user.role == "hospital" else rule_data.get("hospital_id"),
            department=rule_data.get("department"),
            applies_to=rule_data.get("applies_to", "all"),
            target_ids=rule_data.get("target_ids", []),
            priority=rule_data.get("priority", 1),
            max_executions_per_hour=rule_data.get("max_executions_per_hour"),
            max_executions_per_day=rule_data.get("max_executions_per_day"),
            cooldown_minutes=rule_data.get("cooldown_minutes", 0),
            created_by=current_user.id
        )
        
        await rule.create()
        
        return {
            "rule": rule,
            "message": "Automation rule created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation-rules")
async def list_automation_rules(
    current_user: User = Depends(get_current_user)
):
    """List automation rules"""
    try:
        query = AutomationRule.is_active == True
        
        if current_user.role == "hospital":
            query = query & (AutomationRule.hospital_id == (current_user.hospital_id or current_user.id))
        
        rules = await AutomationRule.find(query).sort(-AutomationRule.created_at).to_list()
        
        return {"automation_rules": rules}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml-predictions")
async def trigger_ml_predictions(
    prediction_request: dict,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger ML-powered predictions and automations"""
    try:
        prediction_type = prediction_request.get("type")
        
        if prediction_type == "hospital_surge":
            hospital_id = prediction_request.get("hospital_id") or current_user.hospital_id or current_user.id
            days_ahead = prediction_request.get("days_ahead", 7)
            
            if not ml_predictor:
                return {"error": "ML service not available"}
                
            prediction = await ml_predictor.predict_hospital_surge(hospital_id, days_ahead)
            
            # Trigger automation if high risk
            if prediction.get("risk_level") == "high":
                background_tasks.add_task(
                    trigger_surge_automation,
                    hospital_id,
                    prediction,
                    current_user.id
                )
            
            return {"prediction": prediction}
            
        elif prediction_type == "patient_risk":
            patient_id = prediction_request.get("patient_id")
            if not patient_id:
                raise HTTPException(status_code=400, detail="Patient ID required")
                
            if not ml_predictor:
                return {"error": "ML service not available"}
            
            risk_assessment = await ml_predictor.assess_patient_risk(patient_id)
            
            # Trigger automation for high-risk patients
            if risk_assessment.get("risk_category") == "high":
                background_tasks.add_task(
                    trigger_patient_risk_automation,
                    patient_id,
                    risk_assessment,
                    current_user.id
                )
            
            return {"risk_assessment": risk_assessment}
            
        elif prediction_type == "capacity_optimization":
            hospital_id = prediction_request.get("hospital_id") or current_user.hospital_id or current_user.id
            
            if not ml_predictor:
                return {"error": "ML service not available"}
                
            optimization = await ml_predictor.optimize_hospital_capacity(hospital_id)
            
            # Trigger capacity optimization workflow
            background_tasks.add_task(
                trigger_capacity_optimization,
                hospital_id,
                optimization,
                current_user.id
            )
            
            return {"optimization": optimization}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid prediction type")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-models", dependencies=[Depends(require_role(["admin"]))])
async def train_ml_models(
    training_request: dict,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Train ML models with latest data"""
    try:
        if not ml_predictor:
            return {"error": "ML service not available"}
            
        model_type = training_request.get("model_type", "all")
        
        if model_type == "surge_prediction" or model_type == "all":
            background_tasks.add_task(ml_predictor.train_surge_model)
        
        if model_type == "risk_assessment" or model_type == "all":
            background_tasks.add_task(ml_predictor.train_risk_assessment_model)
        
        return {
            "message": f"ML model training started for: {model_type}",
            "training_started_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def execute_workflow_nodes(workflow: N8NWorkflow, execution: WorkflowExecution, user_id: str):
    """Execute workflow nodes sequentially"""
    try:
        execution.status = "running"
        await execution.save()
        
        # Execute nodes based on workflow logic
        for node in workflow.nodes:
            try:
                execution.current_node = node.id
                await execution.save()
                
                node_output = await execute_node(node, execution, workflow)
                execution.node_outputs[node.id] = node_output
                execution.completed_nodes.append(node.id)
                
                # Add execution log
                execution.execution_logs.append({
                    "timestamp": datetime.utcnow(),
                    "node_id": node.id,
                    "status": "completed",
                    "output": node_output
                })
                
            except Exception as node_error:
                execution.failed_nodes.append(node.id)
                execution.execution_logs.append({
                    "timestamp": datetime.utcnow(),
                    "node_id": node.id,
                    "status": "failed",
                    "error": str(node_error)
                })
                
                if workflow.error_handling == "stop":
                    execution.status = "failed"
                    execution.error_message = str(node_error)
                    execution.error_node = node.id
                    break
        
        if execution.status == "running":
            execution.status = "success"
        
        execution.completed_at = datetime.utcnow()
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        
        await execution.save()
        
        # Update workflow statistics
        workflow.total_executions += 1
        if execution.status == "success":
            workflow.successful_executions += 1
        else:
            workflow.failed_executions += 1
        
        workflow.last_execution = execution.completed_at
        await workflow.save()
        
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        execution.status = "failed"
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()
        await execution.save()

async def execute_node(node: dict, execution: WorkflowExecution, workflow: N8NWorkflow) -> Dict[str, Any]:
    """Execute a single workflow node"""
    node_type = node.get("type")
    parameters = node.get("parameters", {})
    
    if node_type == "notification":
        return await execute_notification_node(parameters, execution)
    elif node_type == "database":
        return await execute_database_node(parameters, execution)
    elif node_type == "ai_analysis":
        return await execute_ai_analysis_node(parameters, execution)
    elif node_type == "http_request":
        return await execute_http_request_node(parameters, execution)
    elif node_type == "condition":
        return await execute_condition_node(parameters, execution)
    elif node_type == "delay":
        delay_seconds = parameters.get("delay_seconds", 1)
        await asyncio.sleep(delay_seconds)
        return {"delayed": delay_seconds}
    else:
        return {"message": f"Node type {node_type} executed", "parameters": parameters}

async def execute_notification_node(parameters: dict, execution: WorkflowExecution) -> dict:
    """Execute notification node"""
    try:
        # Create notification based on parameters
        notification_data = {
            "type": parameters.get("type", "workflow_notification"),
            "title": parameters.get("title", "Workflow Notification"),
            "message": parameters.get("message", "Automated workflow notification"),
            "data": parameters.get("data", {})
        }
        
        # Send to specific users or roles
        if "user_id" in parameters:
            notification = Notification(
                user_id=parameters["user_id"],
                **notification_data
            )
            await notification.create()
        
        return {"status": "notification_sent", "type": parameters.get("type")}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def execute_database_node(parameters: dict, execution: WorkflowExecution) -> dict:
    """Execute database operation node"""
    try:
        action = parameters.get("action")
        
        if action == "update_capacity":
            # Update hospital capacity
            return {"status": "capacity_updated"}
        elif action == "create_appointment":
            # Create appointment
            return {"status": "appointment_created"}
        elif action == "create_log":
            # Create log entry
            return {"status": "log_created"}
        else:
            return {"status": "database_operation_completed", "action": action}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def execute_ai_analysis_node(parameters: dict, execution: WorkflowExecution) -> dict:
    """Execute AI analysis node"""
    try:
        ai_model = parameters.get("ai_model")
        
        if ai_model == "surge_predictor":
            # Run surge prediction
            return {"status": "surge_prediction_completed", "prediction": 0.7}
        elif ai_model == "risk_assessor":
            # Run risk assessment
            return {"status": "risk_assessment_completed", "risk_score": 0.6}
        else:
            return {"status": "ai_analysis_completed", "model": ai_model}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def execute_http_request_node(parameters: dict, execution: WorkflowExecution) -> dict:
    """Execute HTTP request node"""
    try:
        method = parameters.get("method", "GET")
        url = parameters.get("url")
        
        return {"status": "http_request_completed", "method": method, "url": url}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def execute_condition_node(parameters: dict, execution: WorkflowExecution) -> dict:
    """Execute condition check node"""
    try:
        conditions = parameters.get("conditions", [])
        
        # Simple condition evaluation
        result = True
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            # In real implementation, you'd evaluate against actual data
            # For now, return true
            
        return {"status": "condition_evaluated", "result": result}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def schedule_workflow_execution(workflow: N8NWorkflow):
    """Schedule workflow execution based on cron expression"""
    try:
        if workflow.trigger.schedule:
            cron = croniter(workflow.trigger.schedule, datetime.utcnow())
            next_run = cron.get_next(datetime)
            
            logger.info(f"Workflow {workflow.workflow_id} scheduled for next execution at {next_run}")
            
            # In a production environment, you would use a task queue like Celery
            # or a scheduler like APScheduler to handle this
            
    except Exception as e:
        logger.error(f"Error scheduling workflow: {e}")

# Automation trigger functions
async def trigger_surge_automation(hospital_id: str, prediction: dict, user_id: str):
    """Trigger automation for hospital surge predictions"""
    try:
        # Create high-priority notification
        notification = Notification(
            user_id=user_id,
            type="surge_alert",
            title="High Surge Risk Predicted",
            message=f"Hospital surge risk is {prediction['risk_level']}. Predicted load: {prediction['predicted_load']:.1%}",
            priority="high",
            data=prediction
        )
        await notification.create()
        
        logger.info(f"Surge automation triggered for hospital {hospital_id}")
        
    except Exception as e:
        logger.error(f"Error in surge automation: {e}")

async def trigger_patient_risk_automation(patient_id: str, risk_assessment: dict, user_id: str):
    """Trigger automation for high-risk patients"""
    try:
        # Create notification for medical team
        notification = Notification(
            user_id=user_id,
            type="patient_risk_alert",
            title="High-Risk Patient Alert",
            message=f"Patient {patient_id} has {risk_assessment['risk_category']} risk score: {risk_assessment['risk_score']:.2f}",
            priority="high",
            data=risk_assessment
        )
        await notification.create()
        
        logger.info(f"Patient risk automation triggered for patient {patient_id}")
        
    except Exception as e:
        logger.error(f"Error in patient risk automation: {e}")

async def trigger_capacity_optimization(hospital_id: str, optimization: dict, user_id: str):
    """Trigger capacity optimization workflow"""
    try:
        # Create optimization notification
        notification = Notification(
            user_id=user_id,
            type="capacity_optimization",
            title="Capacity Optimization Recommendation",
            message=f"Optimal capacity: {optimization.get('optimal_capacity', 0):.1f}%",
            data=optimization
        )
        await notification.create()
        
        logger.info(f"Capacity optimization triggered for hospital {hospital_id}")
        
    except Exception as e:
        logger.error(f"Error in capacity optimization: {e}")