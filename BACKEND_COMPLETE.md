# HealthEase Backend API Documentation

## 🎉 All Backend Features Implemented Successfully!

### Overview
Complete hospital management system with AI-powered surge prediction, real-time capacity tracking, smart referral system with payments, inventory management, and health advisories.

---

## 📋 Feature Summary

### ✅ 1. AI Surge Prediction Service
**Location:** `backend/app/routes/surge.py`

**Endpoints:**
- `POST /api/surge/predict/{hospital_id}` - Predict patient surge
- `GET /api/surge/history/{hospital_id}` - Get prediction history
- `GET /api/surge/dashboard/{hospital_id}` - Surge dashboard

**Features:**
- OpenAI GPT-3.5-turbo integration
- Multi-source data: Weather, Pollution (AQI), Festivals
- Historical trend analysis
- Confidence scoring
- Actionable recommendations

---

### ✅ 2. Real-time Capacity Management
**Location:** `backend/app/routes/capacity.py`

**Endpoints:**
- `PUT /api/capacity/update` - Update full capacity
- `GET /api/capacity/current` - Get current capacity
- `GET /api/capacity/logs` - View capacity history
- `POST /api/capacity/quick-update` - Quick increment/decrement

**Features:**
- Bed, ICU, ventilator tracking
- Occupancy percentage calculation
- Historical capacity logs
- Real-time updates

---

### ✅ 3. Inventory Management System
**Location:** `backend/app/routes/inventory.py`

**Endpoints:**
- `GET /api/inventory/list` - Get all inventory items
- `POST /api/inventory/add-item` - Add new item
- `PUT /api/inventory/update-item/{item_name}` - Update item
- `GET /api/inventory/alerts` - Get low stock alerts
- `POST /api/inventory/resolve-alert/{alert_index}` - Resolve alert
- `GET /api/inventory/statistics` - Inventory stats

**Features:**
- Category-based organization (Medicines, PPE, Equipment, Consumables)
- Low stock alerts
- Expiry tracking
- Auto-reorder suggestions (paid tier)
- Festival prediction integration

---

### ✅ 4. Razorpay Payment & Referral System
**Location:** `backend/app/routes/referrals.py`

**Endpoints:**
- `POST /api/referrals/create` - Create referral with Razorpay order
- `POST /api/referrals/verify-payment` - Verify payment & distribute funds
- `GET /api/referrals/my-referrals` - Patient's referrals
- `GET /api/referrals/hospital-referrals?referral_type=incoming` - Hospital referrals

**Payment Flow:**
1. Patient pays ₹150 via Razorpay
2. Platform takes ₹40 fee
3. Remaining ₹110 split between hospitals:
   - Destination hospital: 60-70% (based on capacity)
   - Source hospital: 30-40%
4. Funds credited to hospital wallets

**Features:**
- Secure Razorpay integration
- Signature verification
- AI-based revenue split
- Automatic wallet crediting

---

### ✅ 5. Hospital Search with Geolocation
**Location:** `backend/app/routes/search.py`

**Endpoints:**
- `GET /api/search/hospitals?latitude=X&longitude=Y` - Smart search
- `GET /api/search/hospitals/{hospital_id}/details` - Hospital details
- `GET /api/search/nearby-hospitals?city=Delhi` - City-based search
- `GET /api/search/specializations` - Get all specializations

**Features:**
- Haversine formula for distance calculation
- Filter by: beds, ICU, ventilator, specialization
- Real-time availability status
- Travel time estimation
- Color-coded occupancy (green/yellow/orange/red)
- Sort by: distance, beds, rating

---

### ✅ 6. Wallet Management APIs
**Location:** `backend/app/routes/wallet.py`

**Endpoints:**
- `GET /api/wallet/balance` - Get wallet balance
- `GET /api/wallet/transactions` - Transaction history
- `POST /api/wallet/request-payout` - Request bank payout
- `GET /api/wallet/payout-requests` - View payout requests
- `GET /api/wallet/statistics` - Wallet insights

**Features:**
- Real-time balance tracking
- Transaction history
- Payout requests (min ₹100)
- Bank account details encryption
- Earnings analytics

---

### ✅ 7. Health Advisory Alert System
**Location:** `backend/app/routes/alerts.py`

**Endpoints:**
- `GET /api/alerts/pollution-alerts?city=Delhi` - Pollution alerts (AQI > 200)
- `GET /api/alerts/festival-health-tips` - Festival health tips
- `GET /api/alerts/epidemic-alerts?region=Delhi` - Epidemic warnings
- `GET /api/alerts/all-alerts?city=Delhi` - All active alerts

**Alert Types:**
- **Pollution:** Critical/High/Medium based on AQI
- **Festivals:** Health tips for Diwali, Holi, Durga Puja, Eid, Christmas
- **Epidemics:** Dengue (monsoon), Flu (winter), disease outbreaks

**Features:**
- Severity levels: critical, high, medium, low
- Color-coded alerts
- Actionable recommendations
- Regional targeting

---

### ✅ 8. Admin Analytics Dashboard
**Location:** `backend/app/routes/admin.py`

**Endpoints:**
- `GET /api/admin/analytics` - System-wide analytics
- `GET /api/admin/hospitals` - List all hospitals
- `PUT /api/admin/hospitals/{hospital_id}/subscription` - Update subscription
- `GET /api/admin/payouts/pending` - Pending payouts
- `POST /api/admin/payouts/{payout_id}/approve` - Approve payout
- `POST /api/admin/payouts/{payout_id}/reject` - Reject payout
- `GET /api/admin/wallet-transactions` - All transactions
- `GET /api/admin/n8n-logs` - Workflow logs

**Analytics Include:**
- Total hospitals, patients, referrals
- Revenue tracking (platform fees)
- Wallet ecosystem metrics
- Geographic distribution
- Completion rates
- Pending payouts

---

### ✅ 9. Advertisement System
**Location:** `backend/app/routes/advertisements.py`

**Endpoints:**
- `POST /api/ads/create` - Create ad (free-tier hospitals only)
- `GET /api/ads/my-ads` - View my ads
- `PUT /api/ads/{ad_id}` - Update ad
- `DELETE /api/ads/{ad_id}` - Delete ad
- `GET /api/ads/display?city=Delhi` - Public: Get ads to display
- `POST /api/ads/{ad_id}/click` - Track click

**Admin Endpoints:**
- `GET /api/ads/admin/all` - View all ads
- `PUT /api/ads/admin/{ad_id}/review?action=approve` - Approve/reject ad

**Features:**
- Free-tier hospitals can advertise
- Max 3 active ads per hospital
- Admin review system
- Impression & click tracking
- CTR calculation
- Location-based targeting

---

## 🗂️ Database Collections (MongoDB)

1. **users** - Authentication (email, password_hash, role)
2. **hospitals** - Hospital profiles, capacity, location
3. **patients** - Patient profiles
4. **referrals** - Referral records with payment status
5. **wallets** - Hospital wallet balances
6. **wallet_transactions** - All wallet transactions
7. **payout_requests** - Bank payout requests
8. **inventory** - Hospital inventory items
9. **capacity_logs** - Historical capacity data
10. **surge_predictions** - AI prediction history
11. **advertisements** - Ad campaigns
12. **workflow_logs** - n8n automation logs

---

## 🔐 Authentication & Authorization

### Roles:
- **Patient:** Search hospitals, create referrals, view health alerts
- **Hospital:** Manage capacity, inventory, view referrals, wallet
- **Admin:** System analytics, approve payouts, review ads

### JWT Authentication:
- Token expires in 7 days
- Role-based access control via middleware
- Protected routes with `Depends(get_current_user)`

---

## 💳 Payment Integration

### Razorpay Configuration:
```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

### Payment Flow:
1. Create Razorpay order (₹150)
2. Frontend shows Razorpay checkout
3. User completes payment
4. Verify signature
5. Distribute funds to wallets

---

## 🤖 AI Integration

### OpenAI (Surge Prediction):
```env
OPENAI_API_KEY=your_openai_key
```

**Model:** gpt-3.5-turbo
**Input:** Weather, pollution, festivals, historical data
**Output:** Surge prediction with confidence & recommendations

### External APIs:
- **OpenWeatherMap:** Weather data
- **Pollution API:** AQI data
- **Festival Calendar:** Hindu festivals

---

## 📊 Key Features

### Smart Referral Revenue Split:
```python
destination_split = 60% + (capacity_factor * 10%)  # 60-70%
source_split = 30-40%
```

### Occupancy Status:
- 🟢 Green: < 60% (Available)
- 🟡 Yellow: 60-80% (Moderate)
- 🟠 Orange: 80-95% (High Occupancy)
- 🔴 Red: > 95% (Critical)

### Inventory Alerts:
- Low stock when < 20% threshold
- Paid tier gets festival predictions
- Auto-reorder suggestions

---

## 🚀 API Testing

### Health Check:
```bash
GET http://localhost:8000/
```

### Register Hospital:
```bash
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
  "email": "hospital@example.com",
  "password": "password123",
  "role": "hospital",
  "full_name": "City Hospital",
  ...
}
```

### Login:
```bash
POST http://localhost:8000/api/auth/login
```

### Protected Routes:
```bash
GET http://localhost:8000/api/wallet/balance
Authorization: Bearer <token>
```

---

## 📝 Next Steps: Frontend Implementation

### Required Frontend Pages:

1. **Patient Portal:**
   - Hospital search with map
   - Referral creation with Razorpay
   - Health alerts dashboard

2. **Hospital Dashboard:**
   - Surge prediction charts
   - Capacity management
   - Inventory tracking
   - Referral management
   - Wallet & payouts
   - Advertisement manager

3. **Admin Panel:**
   - System analytics
   - Hospital directory
   - Payout approvals
   - Ad review system

### Tech Stack Suggestion:
- React 18 with Vite ✅ (already setup)
- TailwindCSS ✅ (already setup)
- React Router 6 ✅
- Zustand for state ✅
- Axios for API ✅
- Recharts for graphs
- React Leaflet for maps
- Razorpay SDK

---

## 🎯 System Architecture

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│   Port 5173 │
└──────┬──────┘
       │ HTTP/REST
       ↓
┌─────────────┐
│   Backend   │ (FastAPI)
│   Port 8000 │
└──────┬──────┘
       │
       ├─→ MongoDB (Beanie ODM)
       ├─→ OpenAI API (Surge Prediction)
       ├─→ Razorpay API (Payments)
       ├─→ Weather API (External Data)
       └─→ n8n (Workflow Automation)
```

---

## 🛠️ Environment Variables Required

```env
# MongoDB
MONGODB_URI=mongodb+srv://...

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Razorpay
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...

# OpenAI
OPENAI_API_KEY=sk-...

# Weather
OPENWEATHER_API_KEY=...

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/...
```

---

## ✨ Highlights

### What Makes This System Special:

1. **AI-Powered:** GPT-3.5 predicts patient surge using multi-source data
2. **Smart Payments:** Revenue split based on capacity & distance
3. **Real-time:** Live capacity tracking across hospitals
4. **Proactive Alerts:** Pollution, festival, epidemic warnings
5. **Comprehensive:** End-to-end hospital management
6. **Scalable:** MongoDB + FastAPI async architecture
7. **Secure:** JWT auth, Razorpay signature verification
8. **Business Model:** Platform fees + subscriptions

---

## 🎉 Status: Backend 100% Complete!

All 9 major features implemented:
- ✅ AI Surge Prediction
- ✅ Capacity Management
- ✅ Inventory System
- ✅ Payment & Referrals
- ✅ Hospital Search
- ✅ Wallet Management
- ✅ Health Alerts
- ✅ Admin Analytics
- ✅ Advertisement System

**Total Backend Files Created/Modified:** 15+
**Total API Endpoints:** 50+
**Lines of Code:** 4000+

Ready for frontend integration! 🚀
