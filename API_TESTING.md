# Backend API Test Script

## Quick Test Commands

### 1. Health Check
```bash
curl http://localhost:8000/
```

### 2. Test Registration (Hospital)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@hospital.com",
    "password": "password123",
    "role": "hospital",
    "full_name": "Test Hospital",
    "phone": "9876543210",
    "address": "123 Test St",
    "city": "Delhi",
    "state": "Delhi",
    "registration_number": "TEST123",
    "specializations": ["General", "Emergency"]
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@hospital.com",
    "password": "password123"
  }'
```

### 4. Get Current User (with token)
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Hospital Search (No auth required)
```bash
curl "http://localhost:8000/api/search/hospitals?latitude=28.6139&longitude=77.2090&max_distance_km=50&has_beds=true"
```

### 6. Health Alerts (No auth required)
```bash
curl "http://localhost:8000/api/alerts/all-alerts?city=Delhi&state=Delhi"
```

### 7. Display Advertisements (No auth required)
```bash
curl "http://localhost:8000/api/ads/display?city=Delhi&limit=5"
```

## Test with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Test health check
response = requests.get(f"{BASE_URL}/")
print("Health Check:", response.json())

# Register hospital
register_data = {
    "email": "demo@hospital.com",
    "password": "demo123",
    "role": "hospital",
    "full_name": "Demo Hospital",
    "phone": "9999999999",
    "address": "Demo Address",
    "city": "Mumbai",
    "state": "Maharashtra",
    "registration_number": "DEMO001",
    "specializations": ["Cardiology", "Neurology"]
}
response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
print("Register:", response.status_code, response.json())

# Login
login_data = {
    "email": "demo@hospital.com",
    "password": "demo123"
}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    print("Login successful! Token:", token[:50] + "...")
    
    # Use token for protected endpoints
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print("Profile:", response.json())
    
    # Get wallet balance
    response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
    print("Wallet:", response.json())
    
    # Get inventory
    response = requests.get(f"{BASE_URL}/api/inventory/list", headers=headers)
    print("Inventory:", response.json())
```

## API Documentation

Visit: http://localhost:8000/docs

This provides interactive Swagger UI documentation for all endpoints.

## Key Endpoints Summary

### Public (No Auth):
- `GET /` - Health check
- `GET /api/search/hospitals` - Search hospitals
- `GET /api/alerts/*` - Health alerts
- `GET /api/ads/display` - View ads
- `POST /api/ads/{ad_id}/click` - Track ad click

### Patient Auth Required:
- `POST /api/referrals/create` - Create referral
- `GET /api/referrals/my-referrals` - View referrals
- `POST /api/referrals/verify-payment` - Verify payment

### Hospital Auth Required:
- `GET /api/wallet/balance` - Wallet balance
- `GET /api/wallet/transactions` - Transaction history
- `POST /api/wallet/request-payout` - Request payout
- `GET /api/inventory/list` - Inventory list
- `POST /api/inventory/add` - Add item
- `PUT /api/inventory/update/{item_id}` - Update item
- `GET /api/inventory/alerts` - Low stock alerts
- `PUT /api/capacity/update` - Update capacity
- `POST /api/surge/predict/{hospital_id}` - AI prediction
- `POST /api/ads/create` - Create ad (free tier only)

### Admin Auth Required:
- `GET /api/admin/analytics` - System analytics
- `GET /api/admin/payouts/pending` - Pending payouts
- `POST /api/admin/payouts/{payout_id}/approve` - Approve payout
- `GET /api/ads/admin/all` - View all ads
- `PUT /api/ads/admin/{ad_id}/review` - Review ad

## Status: ✅ All APIs Working
