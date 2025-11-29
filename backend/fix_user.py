import asyncio
from app.database import connect_to_mongo
from app.models.user import User
from app.models.hospital import Hospital
from bson import ObjectId

async def fix_user():
    print("Connecting to database...")
    await connect_to_mongo()
    
    email = "test@test.com"
    print(f"Looking for user {email}...")
    user = await User.find_one(User.email == email)
    
    if not user:
        print("User not found!")
        return

    print(f"User found. Role: {user.role}, Hospital ID: {user.hospital_id}")
    
    if not user.hospital_id:
        print("User has no hospital_id. Finding a hospital...")
        hospital = await Hospital.find_one({})
        if hospital:
            print(f"Linking to hospital: {hospital.name} ({hospital.id})")
            user.hospital_id = str(hospital.id)
            user.role = "hospital" # Ensure role is hospital
            await user.save()
            print("User updated successfully.")
        else:
            print("No hospitals found in database to link!")
    else:
        print("User already has a hospital_id.")

if __name__ == "__main__":
    asyncio.run(fix_user())
