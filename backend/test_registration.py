import requests
import json

url = "http://localhost:8000/api/auth/register"

payload = {
    "email": "testuser@example.com",
    "password": "Test1234",
    "role": "patient",
    "profile_data": {
        "full_name": "Test User",
        "phone": "9876543210",
        "date_of_birth": "1990-01-01",
        "blood_group": "O+",
        "address": "123 Test St",
        "city": "Test City",
        "state": "Test State"
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
