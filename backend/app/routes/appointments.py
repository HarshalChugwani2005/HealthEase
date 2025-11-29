from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.hospital import Hospital
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.middleware.auth import get_patient_user, get_hospital_user
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
from beanie.operators import In

router = APIRouter(prefix="/appointments", tags=["Appointments"])

class CreateAppointmentRequest(BaseModel):
    hospital_id: str
    specialization: str
    appointment_type: AppointmentType
    scheduled_time: datetime
    patient_notes: Optional[str] = None

class UpdateAppointmentRequest(BaseModel):
    status: Optional[AppointmentStatus] = None
    doctor_notes: Optional[str] = None

@router.post("/")
async def create_appointment(
    appointment_data: CreateAppointmentRequest,
    current_user: User = Depends(get_patient_user)
):
    """Patient creates an appointment"""
    try:
        if not current_user.profile_id:
            raise HTTPException(status_code=403, detail="User does not have a patient profile.")
            
        hospital = await Hospital.get(ObjectId(appointment_data.hospital_id))
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
            
        # Check if slot is available (simplified - in production, implement proper slot management)
        existing = await Appointment.find_one(
            Appointment.hospital_id == ObjectId(appointment_data.hospital_id),
            Appointment.scheduled_time == appointment_data.scheduled_time,
            In(Appointment.status, [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        )
        
        if existing:
            raise HTTPException(status_code=400, detail="Time slot not available")
            
        appointment = Appointment(
            patient_id=ObjectId(current_user.profile_id),
            hospital_id=ObjectId(appointment_data.hospital_id),
            specialization=appointment_data.specialization,
            appointment_type=appointment_data.appointment_type,
            scheduled_time=appointment_data.scheduled_time,
            patient_notes=appointment_data.patient_notes
        )
        
        # Generate meeting URL for telemedicine
        if appointment_data.appointment_type == AppointmentType.TELEMEDICINE:
            appointment.meeting_id = str(uuid.uuid4())
            appointment.meeting_url = f"https://healthease.meet/{appointment.meeting_id}"
            
        await appointment.insert()
        
        # Create notification for hospital
        # This assumes the hospital has a primary user account to receive notifications
        # A more robust system might have a list of users for a hospital
        hospital_user = await User.find_one(User.hospital_id == str(hospital.id))
        if hospital_user:
            notification = Notification(
                user_id=hospital_user.id,
                type=NotificationType.REFERRAL_UPDATE,
                title="New Appointment Request",
                message=f"New {appointment_data.appointment_type} appointment for {appointment_data.specialization}",
                data={"appointment_id": str(appointment.id)}
            )
            await notification.insert()
        
        return {
            "appointment_id": str(appointment.id),
            "status": appointment.status,
            "scheduled_time": appointment.scheduled_time.isoformat(),
            "meeting_url": appointment.meeting_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-appointments")
async def get_my_appointments(
    current_user: User = Depends(get_patient_user)
):
    """Get patient's appointments"""
    try:
        if not current_user.profile_id:
            raise HTTPException(status_code=403, detail="User does not have a patient profile.")
            
        appointments = await Appointment.find(
            Appointment.patient_id == ObjectId(current_user.profile_id)
        ).sort("-scheduled_time").to_list()
        
        result = []
        for apt in appointments:
            hospital = await Hospital.get(apt.hospital_id)
            result.append({
                "id": str(apt.id),
                "hospital_name": hospital.name if hospital else "Unknown",
                "specialization": apt.specialization,
                "appointment_type": apt.appointment_type,
                "scheduled_time": apt.scheduled_time.isoformat(),
                "status": apt.status,
                "meeting_url": apt.meeting_url,
                "doctor_notes": apt.doctor_notes
            })
            
        return {"appointments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hospital-appointments")
async def get_hospital_appointments(
    current_user: User = Depends(get_hospital_user)
):
    """Get hospital's appointments"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(status_code=403, detail="User is not associated with a hospital.")
            
        hospital_id = ObjectId(current_user.hospital_id)
        appointments = await Appointment.find(
            Appointment.hospital_id == hospital_id
        ).sort("-scheduled_time").to_list()
        
        return {
            "appointments": [
                {
                    "id": str(apt.id),
                    "specialization": apt.specialization,
                    "appointment_type": apt.appointment_type,
                    "scheduled_time": apt.scheduled_time.isoformat(),
                    "status": apt.status,
                    "patient_notes": apt.patient_notes,
                    "meeting_url": apt.meeting_url
                }
                for apt in appointments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    update_data: UpdateAppointmentRequest,
    current_user: User = Depends(get_hospital_user)
):
    """Hospital updates appointment status"""
    try:
        if not current_user.hospital_id:
            raise HTTPException(status_code=403, detail="User is not associated with a hospital.")
            
        appointment = await Appointment.get(ObjectId(appointment_id))
        if not appointment or str(appointment.hospital_id) != current_user.hospital_id:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        if update_data.status:
            appointment.status = update_data.status
        if update_data.doctor_notes:
            appointment.doctor_notes = update_data.doctor_notes
            
        appointment.updated_at = datetime.utcnow()
        await appointment.save()
        
        # Notify patient about status change
        if update_data.status:
            # The patient's user ID is on the appointment document
            patient_user = await User.find_one(User.profile_id == str(appointment.patient_id))
            if patient_user:
                notification = Notification(
                    user_id=patient_user.id,
                    type=NotificationType.APPOINTMENT_REMINDER,
                    title="Appointment Update",
                    message=f"Your appointment status changed to {update_data.status.value}",
                    data={"appointment_id": str(appointment.id)}
                )
                await notification.insert()
        
        return {"message": "Appointment updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))