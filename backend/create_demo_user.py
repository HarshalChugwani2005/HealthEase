import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserRole
from app.utils.validators import hash_password
from app.models.patient import Patient

async def main():
    await connect_to_mongo()
    
    email = "demo@healthease.local"
    password = "demo1234"
    
    existing = await User.find_one(User.email == email)
    if existing:
        print("User already exists")
        return

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.PATIENT,
        is_active=True
    )
    await user.insert()
    
    patient = Patient(
        user_id=user.id,
        full_name="Demo Patient",
        phone="1234567890",
        date_of_birth="1990-01-01",
        blood_group="O+",
        address="123 Health St",
        city="Medi City",
        state="Wellness State"
    )
    await patient.insert()
    
    print(f"Created user {email}")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
