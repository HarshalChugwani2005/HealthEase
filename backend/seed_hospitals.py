"""
Seed script to populate database with sample hospitals for testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

# Sample hospitals near Mumbai/Navi Mumbai area (19.0841, 72.8990)
SAMPLE_HOSPITALS = [
    {
        "name": "Apollo Hospital Navi Mumbai",
        "address": "Plot No. 13, Parsik Hill Road, Sector 23",
        "city": "Navi Mumbai",
        "state": "Maharashtra",
        "pincode": "400614",
        "phone": "+91-22-27827000",
        "email": "apollo.navimumbai@apollohospitals.com",
        "location": {
            "type": "Point",
            "coordinates": [73.0297, 19.0330]  # [longitude, latitude]
        },
        "specializations": ["Cardiology", "Neurology", "Orthopedics", "Emergency", "ICU"],
        "capacity": {
            "total_beds": 250,
            "available_beds": 45,
            "occupied_beds": 205,
            "icu_beds": 40,
            "available_icu_beds": 8,
            "ventilators": 20,
            "available_ventilators": 4
        },
        "subscription": {
            "plan": "paid",
            "started_at": datetime.utcnow()
        },
        "rating": 4.5,
        "review_count": 120,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Fortis Hospital Vashi",
        "address": "Sector 10A, Vashi",
        "city": "Navi Mumbai",
        "state": "Maharashtra",
        "pincode": "400703",
        "phone": "+91-22-71066666",
        "email": "vashi@fortishealthcare.com",
        "location": {
            "type": "Point",
            "coordinates": [72.9981, 19.0667]
        },
        "specializations": ["Cardiology", "Oncology", "Nephrology", "Emergency"],
        "capacity": {
            "total_beds": 180,
            "available_beds": 32,
            "occupied_beds": 148,
            "icu_beds": 25,
            "available_icu_beds": 5,
            "ventilators": 15,
            "available_ventilators": 3
        },
        "subscription": {
            "plan": "paid",
            "started_at": datetime.utcnow()
        },
        "rating": 4.3,
        "review_count": 95,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "MGM Hospital CBD Belapur",
        "address": "Sector 11, CBD Belapur",
        "city": "Navi Mumbai",
        "state": "Maharashtra",
        "pincode": "400614",
        "phone": "+91-22-27576262",
        "email": "info@mgmhospital.co.in",
        "location": {
            "type": "Point",
            "coordinates": [73.0393, 19.0176]
        },
        "specializations": ["General Medicine", "Surgery", "Pediatrics", "Emergency"],
        "capacity": {
            "total_beds": 120,
            "available_beds": 28,
            "occupied_beds": 92,
            "icu_beds": 15,
            "available_icu_beds": 6,
            "ventilators": 8,
            "available_ventilators": 2
        },
        "subscription": {
            "plan": "free"
        },
        "rating": 4.0,
        "review_count": 65,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Kharghar Multispeciality Hospital",
        "address": "Sector 20, Kharghar",
        "city": "Navi Mumbai",
        "state": "Maharashtra",
        "pincode": "410210",
        "phone": "+91-22-27742000",
        "email": "info@khargharhospital.com",
        "location": {
            "type": "Point",
            "coordinates": [73.0660, 19.0428]
        },
        "specializations": ["Cardiology", "Orthopedics", "General Surgery", "ICU"],
        "capacity": {
            "total_beds": 150,
            "available_beds": 55,
            "occupied_beds": 95,
            "icu_beds": 20,
            "available_icu_beds": 12,
            "ventilators": 12,
            "available_ventilators": 6
        },
        "subscription": {
            "plan": "paid",
            "started_at": datetime.utcnow()
        },
        "rating": 4.2,
        "review_count": 78,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Paramount Hospital Panvel",
        "address": "Plot No. 10, Sector 1, New Panvel",
        "city": "Panvel",
        "state": "Maharashtra",
        "pincode": "410206",
        "phone": "+91-22-27462100",
        "email": "info@paramounthospital.in",
        "location": {
            "type": "Point",
            "coordinates": [73.1169, 18.9894]
        },
        "specializations": ["Emergency", "Trauma Care", "General Medicine", "Surgery"],
        "capacity": {
            "total_beds": 100,
            "available_beds": 38,
            "occupied_beds": 62,
            "icu_beds": 12,
            "available_icu_beds": 8,
            "ventilators": 6,
            "available_ventilators": 4
        },
        "subscription": {
            "plan": "free"
        },
        "rating": 3.8,
        "review_count": 45,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]


async def seed_hospitals():
    """Seed hospitals into database"""
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    hospitals_collection = db.hospitals
    
    try:
        # Check if hospitals already exist
        existing_count = await hospitals_collection.count_documents({})
        print(f"Found {existing_count} existing hospitals in database")
        
        if existing_count > 0:
            response = input("Database already has hospitals. Clear and reseed? (y/n): ")
            if response.lower() == 'y':
                await hospitals_collection.delete_many({})
                print("Cleared existing hospitals")
            else:
                print("Keeping existing data")
                return
        
        # Insert sample hospitals
        result = await hospitals_collection.insert_many(SAMPLE_HOSPITALS)
        print(f"✓ Successfully inserted {len(result.inserted_ids)} hospitals")
        
        # Create geospatial index
        await hospitals_collection.create_index([("location", "2dsphere")])
        print("✓ Created geospatial index")
        
        print("\nSample Hospitals Added:")
        for hospital in SAMPLE_HOSPITALS:
            print(f"  - {hospital['name']} ({hospital['city']})")
            print(f"    Available Beds: {hospital['capacity']['available_beds']}")
            print(f"    Specializations: {', '.join(hospital['specializations'][:3])}")
            print()
            
    except Exception as e:
        print(f"✗ Error seeding hospitals: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Hospital Database Seeder")
    print("=" * 60)
    asyncio.run(seed_hospitals())
    print("Done!")
