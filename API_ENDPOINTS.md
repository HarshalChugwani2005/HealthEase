# HealthEase API Endpoints Reference

## Authentication (`/api/auth`)
- `POST /api/auth/register` - Register new user (patient/hospital/admin)
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

---

## Hospital Management (`/api/hospital`)
- `GET /api/hospital/profile` - Get hospital profile
- `PUT /api/hospital/profile` - Update hospital profile
- `GET /api/hospital/capacity` - Get current capacity
- `PUT /api/hospital/capacity` - Update capacity

---

## Patient Management (`/api/patient`)
- `GET /api/patient/profile` - Get patient profile
- `PUT /api/patient/profile` - Update patient profile

---

## AI Surge Prediction (`/api/surge`)
- `POST /api/surge/predict/{hospital_id}` - Get AI surge prediction
- `GET /api/surge/history/{hospital_id}` - View prediction history
- `GET /api/surge/dashboard/{hospital_id}` - Surge dashboard with insights

---

## Capacity Management (`/api/capacity`)
- `PUT /api/capacity/update` - Update full capacity details
- `GET /api/capacity/current` - Get current capacity
- `GET /api/capacity/logs` - View capacity change logs
- `POST /api/capacity/quick-update` - Quick increment/decrement

**Quick Update Body:**
```json
{
  "field": "available_beds",
  "action": "increment",  // or "decrement"
  "value": 5
}
```

---

## Inventory Management (`/api/inventory`)
- `GET /api/inventory/list` - Get all inventory items
- `POST /api/inventory/add-item` - Add new inventory item
- `PUT /api/inventory/update-item/{item_name}` - Update item quantity
- `GET /api/inventory/alerts` - Get low stock alerts
- `POST /api/inventory/resolve-alert/{alert_index}` - Mark alert as resolved
- `GET /api/inventory/statistics` - Get inventory statistics

**Add Item Body:**
```json
{
  "item_name": "Paracetamol",
  "category": "medicines",
  "quantity": 1000,
  "unit": "tablets",
  "reorder_threshold": 200,
  "expiry_date": "2025-12-31"
}
```

---

## Referrals & Payments (`/api/referrals`)
- `POST /api/referrals/create` - Create referral (generates Razorpay order)
- `POST /api/referrals/verify-payment` - Verify payment & distribute funds
- `GET /api/referrals/my-referrals` - Get patient's referrals
- `GET /api/referrals/hospital-referrals?referral_type=incoming` - Get hospital referrals

**Create Referral Body:**
```json
{
  "source_hospital_id": "hospital_id_1",
  "destination_hospital_id": "hospital_id_2",
  "patient_notes": "Requires ICU bed"
}
```

**Response includes:**
```json
{
  "referral_id": "ref_123",
  "razorpay_order_id": "order_xyz",
  "razorpay_key_id": "rzp_test_...",
  "amount": 150
}
```

---

## Hospital Search (`/api/search`)
- `GET /api/search/hospitals?latitude=X&longitude=Y` - Smart geolocation search
- `GET /api/search/hospitals/{hospital_id}/details` - Hospital details
- `GET /api/search/nearby-hospitals?city=Delhi` - City-based search
- `GET /api/search/specializations` - Get all specializations

**Search Query Parameters:**
```
latitude=28.6139
longitude=77.2090
max_distance_km=50
specialization=Cardiology
has_beds=true
has_icu=false
has_ventilator=false
sort_by=distance  // distance, beds, rating
limit=20
```

---

## Wallet Management (`/api/wallet`)
- `GET /api/wallet/balance` - Get wallet balance
- `GET /api/wallet/transactions?limit=50&skip=0` - Transaction history
- `POST /api/wallet/request-payout` - Request bank payout
- `GET /api/wallet/payout-requests` - View payout requests
- `GET /api/wallet/statistics` - Wallet insights

**Request Payout Body:**
```json
{
  "amount": 500,
  "account_holder_name": "Hospital Name",
  "account_number": "1234567890",
  "ifsc_code": "HDFC0001234",
  "bank_name": "HDFC Bank"
}
```

---

## Health Alerts (`/api/alerts`)
- `GET /api/alerts/pollution-alerts?city=Delhi&state=Delhi` - Pollution alerts
- `GET /api/alerts/festival-health-tips` - Festival health tips
- `GET /api/alerts/epidemic-alerts?region=India` - Epidemic warnings
- `GET /api/alerts/all-alerts?city=Delhi&state=Delhi` - All active alerts

**Alert Response:**
```json
{
  "has_alert": true,
  "alert": {
    "id": "pollution_Delhi_20240115",
    "title": "🚨 SEVERE Air Quality Alert",
    "type": "pollution",
    "severity": "critical",
    "message": "AQI is 450...",
    "recommendations": [
      "Avoid all outdoor activities",
      "Wear N95 masks..."
    ]
  }
}
```

---

## Advertisements (`/api/ads`)

### Hospital Endpoints:
- `POST /api/ads/create` - Create ad (free-tier only)
- `GET /api/ads/my-ads` - View my ads
- `PUT /api/ads/{ad_id}` - Update ad
- `DELETE /api/ads/{ad_id}` - Delete ad

### Public Endpoints:
- `GET /api/ads/display?city=Delhi&limit=5` - Get ads to display
- `POST /api/ads/{ad_id}/click` - Track ad click

### Admin Endpoints:
- `GET /api/ads/admin/all?status_filter=pending` - View all ads
- `PUT /api/ads/admin/{ad_id}/review?action=approve` - Approve/reject

**Create Ad Body:**
```json
{
  "title": "24/7 Emergency Services",
  "description": "Best cardiology care in Delhi",
  "image_url": "https://...",
  "link_url": "https://...",
  "target_audience": "city"  // all, city, state
}
```

---

## Admin Dashboard (`/api/admin`)
- `GET /api/admin/analytics` - System-wide analytics
- `GET /api/admin/hospitals?subscription_plan=paid` - List hospitals
- `PUT /api/admin/hospitals/{hospital_id}/subscription` - Update subscription
- `GET /api/admin/payouts/pending` - Pending payout requests
- `POST /api/admin/payouts/{payout_id}/approve` - Approve payout
- `POST /api/admin/payouts/{payout_id}/reject` - Reject payout
- `GET /api/admin/wallet-transactions?limit=100` - All transactions
- `GET /api/admin/advertisements` - View all ads
- `POST /api/admin/advertisements` - Create ad for hospital

**Analytics Response:**
```json
{
  "overview": {
    "total_hospitals": 150,
    "verified_hospitals": 120,
    "total_patients": 5000,
    "total_referrals": 1200
  },
  "revenue": {
    "total_platform_fees": 48000,
    "currency": "INR"
  },
  "wallets": {
    "total_balance": 132000,
    "pending_payouts": 5,
    "pending_payout_amount": 15000
  }
}
```

---

## Authentication Required

### Headers:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Role Requirements:
- **Patient:** Referral creation, search, alerts
- **Hospital:** Capacity, inventory, wallet, ads (free tier)
- **Admin:** Analytics, payouts, ad review

---

## Testing with cURL

### Register:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@hospital.com",
    "password": "password123",
    "role": "hospital",
    "full_name": "Test Hospital",
    "phone": "9876543210",
    "address": "123 Main St",
    "city": "Delhi",
    "state": "Delhi"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@hospital.com",
    "password": "password123"
  }'
```

### Protected Route:
```bash
curl -X GET http://localhost:8000/api/wallet/balance \
  -H "Authorization: Bearer <token>"
```

---

## Frontend Integration

### Axios Setup:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Usage:
```javascript
// Get surge prediction
const response = await api.post('/api/surge/predict/hospital_id');

// Get hospital search results
const hospitals = await api.get('/api/search/hospitals', {
  params: {
    latitude: 28.6139,
    longitude: 77.2090,
    has_beds: true
  }
});

// Create referral
const referral = await api.post('/api/referrals/create', {
  source_hospital_id: 'id1',
  destination_hospital_id: 'id2',
  patient_notes: 'Urgent'
});
```

---

## Razorpay Integration (Frontend)

```javascript
const options = {
  key: response.razorpay_key_id,
  amount: response.amount * 100, // paise
  currency: "INR",
  name: "HealthEase",
  description: "Hospital Referral Payment",
  order_id: response.razorpay_order_id,
  handler: async function (razorpay_response) {
    // Verify payment
    await api.post('/api/referrals/verify-payment', {
      razorpay_order_id: razorpay_response.razorpay_order_id,
      razorpay_payment_id: razorpay_response.razorpay_payment_id,
      razorpay_signature: razorpay_response.razorpay_signature
    });
  }
};

const rzp = new Razorpay(options);
rzp.open();
```

---

## Error Responses

### Standard Error Format:
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (wrong role)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting & Best Practices

1. Cache hospital search results
2. Debounce search inputs
3. Paginate large lists
4. Use optimistic UI updates
5. Handle network errors gracefully
6. Store JWT token securely
7. Refresh token before expiry

---

**Total Endpoints:** 50+
**Authentication:** JWT Bearer Token
**Base URL:** `http://localhost:8000`

All APIs are async and return JSON responses. ✨
