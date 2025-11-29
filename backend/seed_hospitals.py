import asyncio
import os
from app.database import connect_to_mongo
from app.models.hospital import Hospital
from app.config import settings

# Dummy hospitals in Mumbai
HOSPITALS = [
    {
        "name": "Lilavati Hospital",
        "email": "info@lilavati.com",
        "phone": "+91 22 2675 1000",
        "address": "A-791, Bandra Reclamation, Bandra West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400050",
        "specializations": ["Cardiology", "Neurology", "Orthopedics"],
        "location": {
            "type": "Point",
            "coordinates": [72.8258, 19.0502]  # Longitude, Latitude
        },
        "capacity": {
            "total_beds": 300,
            "available_beds": 45,
            "icu_beds": 50,
            "available_icu_beds": 5,
            "ventilators": 20,
            "available_ventilators": 2
        },
        "subscription": {
            "plan": "premium",
            "is_active": True
        }
    },
    {
        "name": "Nanavati Max Hospital",
        "email": "info@nanavati.com",
        "phone": "+91 22 2626 7500",
        "address": "SV Road, Vile Parle West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400056",
        "specializations": ["Oncology", "Pediatrics", "Gastroenterology"],
        "location": {
            "type": "Point",
            "coordinates": [72.8411, 19.0968]
        },
        "capacity": {
            "total_beds": 350,
            "available_beds": 20,
            "icu_beds": 60,
            "available_icu_beds": 10,
            "ventilators": 25,
            "available_ventilators": 5
        },
        "subscription": {
            "plan": "premium",
            "is_active": True
        }
    },
    {
        "name": "Kokilaben Dhirubhai Ambani Hospital",
        "email": "info@kokilaben.com",
        "phone": "+91 22 3099 9999",
        "address": "Rao Saheb, Achutrao Patwardhan Marg, Four Bungalows, Andheri West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400053",
        "specializations": ["Robotic Surgery", "Transplants", "Rehabilitation"],
        "location": {
            "type": "Point",
            "coordinates": [72.8235, 19.1316]
        },
        "capacity": {
            "total_beds": 750,
            "available_beds": 120,
            "icu_beds": 100,
            "available_icu_beds": 15,
            "ventilators": 40,
            "available_ventilators": 8
        },
        "subscription": {
            "plan": "enterprise",
            "is_active": True
        }
    },
    {
        "name": "H.N. Reliance Foundation Hospital",
        "email": "info@rfhospital.org",
        "phone": "1800 221 166",
        "address": "Prarthana Samaj, Raja Rammohan Roy Rd, Girgaon",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400004",
        "specializations": ["Cardiology", "Oncology", "Neurology"],
        "location": {
            "type": "Point",
            "coordinates": [72.8194, 18.9592]
        },
        "capacity": {
            "total_beds": 345,
            "available_beds": 50,
            "icu_beds": 45,
            "available_icu_beds": 8,
            "ventilators": 15,
            "available_ventilators": 3
        },
        "subscription": {
            "plan": "premium",
            "is_active": True
        }
    },
    {
        "name": "Breach Candy Hospital",
        "email": "info@breachcandy.org",
        "phone": "+91 22 2366 7788",
        "address": "60 A, Bhulabhai Desai Marg",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400026",
        "specializations": ["Maternity", "Cardiology", "Dermatology"],
        "location": {
            "type": "Point",
            "coordinates": [72.8054, 18.9723]
        },
        "capacity": {
            "total_beds": 212,
            "available_beds": 15,
            "icu_beds": 30,
            "available_icu_beds": 2,
            "ventilators": 10,
            "available_ventilators": 0
        },
        "subscription": {
            "plan": "standard",
            "is_active": True
        }
    }
]

async def seed_data():
    print("Connecting to database...")
    await connect_to_mongo()
    
    print("Seeding hospitals...")
    count = 0
    for h_data in HOSPITALS:
        # Check if exists
        existing = await Hospital.find_one(Hospital.name == h_data["name"])
        if not existing:
            hospital = Hospital(**h_data)
            await hospital.insert()
            print(f"Created: {hospital.name}")
            count += 1
        else:
            print(f"Skipped (exists): {h_data['name']}")
    
    print(f"Seeding complete. Added {count} hospitals.")

if __name__ == "__main__":
    asyncio.run(seed_data())
