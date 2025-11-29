from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta, time
from app.models.medication import Medication, MedicationReminder, Prescription, MedicationStatus, MedicationFrequency
from app.models.notification import Notification
from app.middleware.auth import get_current_user, require_role
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/medications", tags=["medications"])

@router.post("/prescriptions", dependencies=[Depends(require_role(["hospital", "admin"]))])
async def create_prescription(
    prescription_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new prescription with medications"""
    try:
        # Generate unique prescription number
        prescription_number = f"RX{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create prescription
        prescription = Prescription(
            patient_id=prescription_data["patient_id"],
            hospital_id=current_user.hospital_id or current_user.id,
            doctor_id=current_user.id,
            prescription_number=prescription_number,
            diagnosis=prescription_data.get("diagnosis"),
            symptoms=prescription_data.get("symptoms", []),
            notes=prescription_data.get("notes")
        )
        
        medications = []
        medication_ids = []
        
        # Create medications from prescription
        for med_data in prescription_data["medications"]:
            medication = Medication(
                patient_id=prescription_data["patient_id"],
                hospital_id=current_user.hospital_id or current_user.id,
                prescribed_by=current_user.id,
                name=med_data["name"],
                generic_name=med_data.get("generic_name"),
                dosage=med_data["dosage"],
                form=med_data["form"],
                frequency=MedicationFrequency(med_data["frequency"]),
                schedule=med_data.get("schedule", []),
                duration_days=med_data.get("duration_days"),
                instructions=med_data["instructions"],
                food_instructions=med_data.get("food_instructions"),
                special_instructions=med_data.get("special_instructions")
            )
            
            await medication.create()
            medications.append(medication)
            medication_ids.append(str(medication.id))
            
            # Create medication reminders
            await create_medication_reminders(medication)
        
        prescription.medications = medication_ids
        await prescription.create()
        
        # Send notification to patient
        notification = Notification(
            user_id=prescription_data["patient_id"],
            type="prescription_issued",
            title="New Prescription Issued",
            message=f"A new prescription has been issued by Dr. {current_user.name}",
            data={
                "prescription_id": str(prescription.id),
                "prescription_number": prescription_number,
                "medications_count": len(medications)
            }
        )
        await notification.create()
        
        return {
            "prescription": prescription,
            "medications": medications,
            "message": "Prescription created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescriptions")
async def get_prescriptions(
    patient_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get prescriptions for patient or doctor"""
    try:
        if current_user.role == "patient":
            prescriptions = await Prescription.find(
                Prescription.patient_id == current_user.id
            ).sort(-Prescription.created_at).to_list()
        elif current_user.role == "hospital" and patient_id:
            prescriptions = await Prescription.find(
                Prescription.patient_id == patient_id,
                Prescription.hospital_id == current_user.hospital_id or current_user.id
            ).sort(-Prescription.created_at).to_list()
        else:
            prescriptions = await Prescription.find(
                Prescription.doctor_id == current_user.id
            ).sort(-Prescription.created_at).to_list()
            
        return {"prescriptions": prescriptions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}")
async def get_patient_medications(
    patient_id: str,
    status: Optional[MedicationStatus] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get medications for a patient"""
    try:
        # Verify access
        if current_user.role == "patient" and current_user.id != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        query = Medication.patient_id == patient_id
        if status:
            query = query & (Medication.status == status)
            
        medications = await Medication.find(query).sort(-Medication.created_at).to_list()
        
        return {"medications": medications}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medications/{medication_id}/taken")
async def mark_medication_taken(
    medication_id: str,
    reminder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Mark medication as taken"""
    try:
        medication = await Medication.get(medication_id)
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
            
        if current_user.role == "patient" and current_user.id != medication.patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Update medication
        medication.last_taken = datetime.utcnow()
        await medication.save()
        
        # Update reminder if provided
        if reminder_id:
            reminder = await MedicationReminder.get(reminder_id)
            if reminder:
                reminder.taken = True
                reminder.acknowledged = True
                reminder.taken_at = datetime.utcnow()
                await reminder.save()
        
        # Create adherence log entry
        # This would be implemented based on your adherence tracking needs
        
        return {"message": "Medication marked as taken", "taken_at": medication.last_taken}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reminders")
async def get_medication_reminders(
    current_user: User = Depends(get_current_user)
):
    """Get upcoming medication reminders for patient"""
    try:
        if current_user.role != "patient":
            raise HTTPException(status_code=403, detail="Only patients can access reminders")
            
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        reminders = await MedicationReminder.find(
            MedicationReminder.patient_id == current_user.id,
            MedicationReminder.scheduled_time >= now,
            MedicationReminder.scheduled_time <= tomorrow,
            MedicationReminder.sent == False,
            MedicationReminder.taken == False
        ).sort(MedicationReminder.scheduled_time).to_list()
        
        return {"reminders": reminders}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medications/{medication_id}/status")
async def update_medication_status(
    medication_id: str,
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update medication status"""
    try:
        medication = await Medication.get(medication_id)
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
            
        # Verify access
        if (current_user.role == "patient" and current_user.id != medication.patient_id) or \
           (current_user.role == "hospital" and current_user.id != medication.prescribed_by):
            raise HTTPException(status_code=403, detail="Access denied")
            
        medication.status = MedicationStatus(status_data["status"])
        if status_data["status"] == "completed":
            medication.end_date = datetime.utcnow()
        elif status_data["status"] == "discontinued":
            medication.end_date = datetime.utcnow()
            
        await medication.save()
        
        return {"message": "Medication status updated", "medication": medication}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence/{patient_id}")
async def get_medication_adherence(
    patient_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get medication adherence statistics"""
    try:
        # Verify access
        if current_user.role == "patient" and current_user.id != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        start_date = datetime.utcnow() - timedelta(days=days)
        
        medications = await Medication.find(
            Medication.patient_id == patient_id,
            Medication.status == MedicationStatus.ACTIVE,
            Medication.start_date <= datetime.utcnow()
        ).to_list()
        
        adherence_stats = []
        overall_adherence = 0
        
        for medication in medications:
            # Get reminders for this medication
            reminders = await MedicationReminder.find(
                MedicationReminder.medication_id == str(medication.id),
                MedicationReminder.scheduled_time >= start_date
            ).to_list()
            
            total_reminders = len(reminders)
            taken_reminders = len([r for r in reminders if r.taken])
            missed_reminders = len([r for r in reminders if r.missed])
            
            if total_reminders > 0:
                adherence_percentage = (taken_reminders / total_reminders) * 100
            else:
                adherence_percentage = 100
                
            adherence_stats.append({
                "medication_name": medication.name,
                "total_doses": total_reminders,
                "taken_doses": taken_reminders,
                "missed_doses": missed_reminders,
                "adherence_percentage": round(adherence_percentage, 2)
            })
            
            overall_adherence += adherence_percentage
            
        if adherence_stats:
            overall_adherence = overall_adherence / len(adherence_stats)
        
        return {
            "patient_id": patient_id,
            "analysis_period_days": days,
            "overall_adherence_percentage": round(overall_adherence, 2),
            "medication_adherence": adherence_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_medication_reminders(medication: Medication):
    """Create reminders for a medication based on its schedule"""
    try:
        # Calculate reminder times based on frequency and schedule
        start_date = medication.start_date or datetime.utcnow()
        end_date = medication.end_date
        
        if not end_date and medication.duration_days:
            end_date = start_date + timedelta(days=medication.duration_days)
        elif not end_date:
            # Default to 30 days if no end date specified
            end_date = start_date + timedelta(days=30)
            
        current_date = start_date.date()
        end_date = end_date.date()
        
        while current_date <= end_date:
            # Create reminders based on schedule
            for schedule in medication.schedule:
                reminder_time = datetime.combine(current_date, schedule.time)
                
                reminder = MedicationReminder(
                    patient_id=medication.patient_id,
                    medication_id=str(medication.id),
                    scheduled_time=reminder_time,
                    medication_name=medication.name,
                    dosage=schedule.dose_amount,
                    instructions=schedule.instructions or medication.instructions
                )
                
                await reminder.create()
                
            current_date += timedelta(days=1)
            
    except Exception as e:
        print(f"Error creating medication reminders: {e}")