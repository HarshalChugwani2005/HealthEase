import asyncio
from app.database import connect_to_mongo
from app.models.user import User, UserRole
from app.models.patient import Patient
from datetime import date

async def fix_patient_profile():
    print("Connecting to database...")
    await connect_to_mongo()
    
    email = "2023.ved.joshi@ves.ac.in"
    print(f"Finding user {email}...")
    
    user = await User.find_one(User.email == email)
    
    if not user:
        print("User not found!")
        return
        
    print(f"User found: {user.id}")
    
    # Check if patient profile already exists
    patient = await Patient.find_one(Patient.user_id == user.id)
    
    if not patient:
        print("Creating new patient profile...")
        patient = Patient(
            user_id=user.id,
            full_name="Ved Joshi",
            phone="+919876543210",
            date_of_birth=date(2003, 1, 1),
            blood_group="B+",
            address="Mumbai, India",
            city="Mumbai",
            state="Maharashtra"
        )
        await patient.insert()
        print(f"Patient profile created: {patient.id}")
    else:
        print(f"Patient profile already exists: {patient.id}")
        
    # Link to user
    user.profile_id = str(patient.id)
    user.role = UserRole.PATIENT
    await user.save()
    print("User updated with profile_id and role.")

if __name__ == "__main__":
    asyncio.run(fix_patient_profile())
