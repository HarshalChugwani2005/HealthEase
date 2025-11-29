import asyncio
import random
from app.database import connect_to_mongo
from app.models.hospital import Hospital
from faker import Faker

fake = Faker('en_IN')

SPECIALIZATIONS = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology",
    "Gastroenterology", "Dermatology", "ENT", "Ophthalmology", "Psychiatry",
    "Urology", "Gynecology", "General Medicine", "Dental"
]

MUMBAI_LOCATIONS = [
    {"name": "Andheri West", "lat": 19.1136, "lng": 72.8697},
    {"name": "Bandra West", "lat": 19.0596, "lng": 72.8295},
    {"name": "Dadar", "lat": 19.0178, "lng": 72.8478},
    {"name": "Colaba", "lat": 18.9067, "lng": 72.8147},
    {"name": "Juhu", "lat": 19.1075, "lng": 72.8263},
    {"name": "Powai", "lat": 19.1187, "lng": 72.9073},
    {"name": "Goregaon", "lat": 19.1663, "lng": 72.8526},
    {"name": "Malad", "lat": 19.1874, "lng": 72.8484},
    {"name": "Borivali", "lat": 19.2312, "lng": 72.8567},
    {"name": "Ghatkopar", "lat": 19.0860, "lng": 72.9090},
    {"name": "Mulund", "lat": 19.1726, "lng": 72.9425},
    {"name": "Thane", "lat": 19.2183, "lng": 72.9781},
    {"name": "Vashi", "lat": 19.0748, "lng": 73.0000},
    {"name": "Chembur", "lat": 19.0522, "lng": 72.9005},
    {"name": "Worli", "lat": 19.0166, "lng": 72.8168}
]

async def seed_random_hospitals():
    print("Connecting to database...")
    await connect_to_mongo()
    
    print("Seeding random hospitals...")
    for loc in MUMBAI_LOCATIONS:
        # Generate random offset for coordinates to avoid stacking
        lat = loc["lat"] + random.uniform(-0.01, 0.01)
        lng = loc["lng"] + random.uniform(-0.01, 0.01)
        
        name = f"{fake.last_name()} {random.choice(['Hospital', 'Medical Center', 'Clinic', 'Nursing Home'])}"
        
        hospital_data = {
            "name": name,
            "email": f"contact@{name.lower().replace(' ', '')}.com",
            "phone": f"+91 {random.randint(7000000000, 9999999999)}",
            "address": f"{random.randint(1, 100)}, {fake.street_name()}, {loc['name']}",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": f"400{random.randint(10, 99)}",
            "specializations": random.sample(SPECIALIZATIONS, k=random.randint(3, 8)),
            "location": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "capacity": {
                "total_beds": random.randint(50, 500),
                "available_beds": random.randint(5, 50),
                "icu_beds": random.randint(10, 50),
                "available_icu_beds": random.randint(1, 10),
                "ventilators": random.randint(5, 20),
                "available_ventilators": random.randint(0, 5)
            },
            "subscription": {
                "plan": random.choice(["free", "premium", "enterprise"]),
                "is_active": True
            },
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(10, 500)
        }
        
        # Check if exists (by name to avoid duplicates if re-run)
        existing = await Hospital.find_one(Hospital.name == name)
        if not existing:
            hospital = Hospital(**hospital_data)
            await hospital.insert()
            print(f"Created: {name} in {loc['name']}")
        else:
            print(f"Skipped: {name} (exists)")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_random_hospitals())
