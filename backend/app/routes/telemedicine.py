from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.telemedicine import TelemedicineSession, IoTDevice, HealthData, EmergencyAlert
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.middleware.auth import get_current_user
from app.models.user import User
import uuid
import json

router = APIRouter(prefix="/api/telemedicine", tags=["telemedicine"])

# WebSocket connection manager for real-time features
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time data from IoT devices, emergency alerts, etc.
            await process_realtime_data(data, user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.post("/sessions")
async def create_telemedicine_session(
    session_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new telemedicine session"""
    try:
        # Get the appointment
        appointment = await Appointment.get(session_data["appointment_id"])
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Verify user can create session
        if current_user.role == "patient" and current_user.id != appointment.patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "hospital" and current_user.id != appointment.hospital_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate session details
        session_id = str(uuid.uuid4())
        room_id = f"room_{session_id[:8]}"
        session_url = f"https://meet.healthease.com/room/{room_id}"
        
        session = TelemedicineSession(
            session_id=session_id,
            appointment_id=session_data["appointment_id"],
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id or current_user.id,
            hospital_id=appointment.hospital_id,
            session_type=session_data.get("session_type", "video_consultation"),
            room_id=room_id,
            session_url=session_url,
            scheduled_start=appointment.appointment_date,
            recording_enabled=session_data.get("recording_enabled", False)
        )
        
        await session.create()
        
        # Send notifications to both patient and doctor
        await send_session_notifications(session)
        
        return {
            "session": session,
            "join_url": session_url,
            "message": "Telemedicine session created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_telemedicine_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get telemedicine session details"""
    try:
        session = await TelemedicineSession.find_one(
            TelemedicineSession.session_id == session_id
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify access
        if (current_user.role == "patient" and current_user.id != session.patient_id) or \
           (current_user.role == "hospital" and current_user.id != session.doctor_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"session": session}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/start")
async def start_telemedicine_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start a telemedicine session"""
    try:
        session = await TelemedicineSession.find_one(
            TelemedicineSession.session_id == session_id
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.status = "active"
        session.actual_start = datetime.utcnow()
        await session.save()
        
        return {
            "message": "Session started",
            "session": session,
            "join_url": session.session_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/end")
async def end_telemedicine_session(
    session_id: str,
    session_data: dict,
    current_user: User = Depends(get_current_user)
):
    """End a telemedicine session"""
    try:
        session = await TelemedicineSession.find_one(
            TelemedicineSession.session_id == session_id
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.status = "completed"
        session.ended_at = datetime.utcnow()
        session.consultation_notes = session_data.get("consultation_notes")
        session.prescriptions_issued = session_data.get("prescriptions_issued", [])
        session.follow_up_required = session_data.get("follow_up_required", False)
        session.follow_up_date = session_data.get("follow_up_date")
        session.patient_satisfaction = session_data.get("patient_satisfaction")
        
        if session.actual_start:
            duration = session.ended_at - session.actual_start
            session.duration_minutes = int(duration.total_seconds() / 60)
        
        await session.save()
        
        # Update appointment status
        appointment = await Appointment.get(session.appointment_id)
        if appointment:
            appointment.status = "completed"
            await appointment.save()
        
        return {"message": "Session ended successfully", "session": session}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/devices/register")
async def register_iot_device(
    device_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Register a new IoT device"""
    try:
        if current_user.role != "patient":
            raise HTTPException(status_code=403, detail="Only patients can register devices")
        
        device = IoTDevice(
            device_id=device_data["device_id"],
            patient_id=current_user.id,
            device_type=device_data["device_type"],
            brand=device_data["brand"],
            model=device_data["model"],
            serial_number=device_data["serial_number"],
            mac_address=device_data.get("mac_address"),
            sync_interval=device_data.get("sync_interval", 300),
            connection_type=device_data.get("connection_type", "bluetooth"),
            location=device_data.get("location")
        )
        
        await device.create()
        
        return {"device": device, "message": "IoT device registered successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_iot_devices(
    current_user: User = Depends(get_current_user)
):
    """Get IoT devices for patient"""
    try:
        if current_user.role != "patient":
            raise HTTPException(status_code=403, detail="Access denied")
        
        devices = await IoTDevice.find(
            IoTDevice.patient_id == current_user.id
        ).to_list()
        
        return {"devices": devices}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/devices/{device_id}/data")
async def submit_health_data(
    device_id: str,
    health_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit health data from IoT device"""
    try:
        device = await IoTDevice.find_one(
            IoTDevice.device_id == device_id
        )
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if current_user.role == "patient" and current_user.id != device.patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create health data record
        data_record = HealthData(
            device_id=device_id,
            patient_id=device.patient_id,
            vital_signs=health_data.get("vital_signs", []),
            raw_data=health_data.get("raw_data", {}),
            recorded_at=datetime.fromisoformat(health_data["recorded_at"]),
            activity_context=health_data.get("activity_context"),
            medication_taken=health_data.get("medication_taken", False),
            notes=health_data.get("notes")
        )
        
        # Check for anomalies and trigger alerts if needed
        alerts_triggered = await check_health_data_alerts(data_record, device)
        data_record.alerts_triggered = alerts_triggered
        
        await data_record.create()
        
        # Update device last sync
        device.last_sync = datetime.utcnow()
        await device.save()
        
        # Send real-time updates to connected clients
        await manager.send_personal_message(
            json.dumps({
                "type": "health_data_update",
                "device_id": device_id,
                "data": health_data
            }),
            device.patient_id
        )
        
        return {
            "message": "Health data recorded successfully",
            "alerts_triggered": alerts_triggered
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-data")
async def get_health_data(
    device_id: Optional[str] = None,
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Get health data for patient"""
    try:
        if current_user.role != "patient":
            raise HTTPException(status_code=403, detail="Access denied")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = HealthData.patient_id == current_user.id
        query = query & (HealthData.recorded_at >= start_date)
        
        if device_id:
            query = query & (HealthData.device_id == device_id)
        
        health_data = await HealthData.find(query).sort(
            -HealthData.recorded_at
        ).to_list()
        
        return {"health_data": health_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-alert")
async def create_emergency_alert(
    alert_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create emergency alert"""
    try:
        alert = EmergencyAlert(
            alert_id=str(uuid.uuid4()),
            patient_id=alert_data["patient_id"],
            device_id=alert_data.get("device_id"),
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            location=alert_data.get("location"),
            coordinates=alert_data.get("coordinates"),
            vital_signs_at_trigger=alert_data.get("vital_signs", {}),
            medical_history_relevant=alert_data.get("medical_history", []),
            current_medications=alert_data.get("current_medications", [])
        )
        
        await alert.create()
        
        # Trigger emergency response protocol
        await trigger_emergency_response(alert)
        
        return {"alert": alert, "message": "Emergency alert created"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emergency-alerts")
async def get_emergency_alerts(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get emergency alerts"""
    try:
        if current_user.role == "patient":
            query = EmergencyAlert.patient_id == current_user.id
        else:
            # Healthcare providers see all active alerts
            query = EmergencyAlert.status == "active"
        
        if status:
            query = query & (EmergencyAlert.status == status)
        
        alerts = await EmergencyAlert.find(query).sort(
            -EmergencyAlert.triggered_at
        ).to_list()
        
        return {"alerts": alerts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def send_session_notifications(session: TelemedicineSession):
    """Send notifications about telemedicine session"""
    try:
        # Notify patient
        patient_notification = Notification(
            user_id=session.patient_id,
            type="telemedicine_session",
            title="Telemedicine Session Ready",
            message="Your telemedicine consultation is ready to join",
            data={
                "session_id": session.session_id,
                "join_url": session.session_url,
                "scheduled_start": session.scheduled_start.isoformat()
            }
        )
        await patient_notification.create()
        
        # Notify doctor
        doctor_notification = Notification(
            user_id=session.doctor_id,
            type="telemedicine_session",
            title="Telemedicine Session Ready",
            message="Patient consultation is ready to join",
            data={
                "session_id": session.session_id,
                "join_url": session.session_url,
                "patient_id": session.patient_id
            }
        )
        await doctor_notification.create()
        
    except Exception as e:
        print(f"Error sending session notifications: {e}")

async def check_health_data_alerts(data_record: HealthData, device: IoTDevice):
    """Check if health data triggers any alerts"""
    alerts_triggered = []
    
    try:
        for vital_sign in data_record.vital_signs:
            # Check against device alert rules
            for rule in device.alert_rules:
                if rule.parameter == vital_sign.type:
                    if rule.condition == "greater_than" and vital_sign.value > rule.threshold_value:
                        alerts_triggered.append(rule.alert_message)
                    elif rule.condition == "less_than" and vital_sign.value < rule.threshold_value:
                        alerts_triggered.append(rule.alert_message)
                    elif rule.condition == "between" and rule.threshold_max:
                        if not (rule.threshold_value <= vital_sign.value <= rule.threshold_max):
                            alerts_triggered.append(rule.alert_message)
        
        # Create emergency alert for critical values
        critical_alerts = [a for a in device.alert_rules if a.severity == "high" and a.alert_message in alerts_triggered]
        
        if critical_alerts:
            emergency_alert = EmergencyAlert(
                alert_id=str(uuid.uuid4()),
                patient_id=device.patient_id,
                device_id=device.device_id,
                alert_type="vital_sign_critical",
                severity="high",
                message=f"Critical vital signs detected: {', '.join([a.alert_message for a in critical_alerts])}",
                vital_signs_at_trigger={vs.type: vs.value for vs in data_record.vital_signs}
            )
            await emergency_alert.create()
            
    except Exception as e:
        print(f"Error checking health data alerts: {e}")
    
    return alerts_triggered

async def trigger_emergency_response(alert: EmergencyAlert):
    """Trigger emergency response protocol"""
    try:
        # This would integrate with emergency services, notify emergency contacts, etc.
        # For now, create high-priority notifications
        
        emergency_notification = Notification(
            user_id=alert.patient_id,
            type="emergency_alert",
            title="Emergency Alert Triggered",
            message=alert.message,
            priority="high",
            data={
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity
            }
        )
        await emergency_notification.create()
        
        # Send real-time alert
        await manager.send_personal_message(
            json.dumps({
                "type": "emergency_alert",
                "alert": {
                    "id": alert.alert_id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message
                }
            }),
            alert.patient_id
        )
        
    except Exception as e:
        print(f"Error triggering emergency response: {e}")

async def process_realtime_data(data: str, user_id: str):
    """Process real-time data from WebSocket"""
    try:
        message = json.loads(data)
        message_type = message.get("type")
        
        if message_type == "health_data":
            # Process real-time health data
            pass
        elif message_type == "emergency":
            # Handle emergency situations
            pass
        
    except Exception as e:
        print(f"Error processing real-time data: {e}")