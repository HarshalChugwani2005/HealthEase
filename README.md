# HealthEase - Agentic AI for Predictive Hospital Management

A centralized, AI-based platform that breaks away from conventional healthcare processes by fusing multi-modal data to create actionable, hyper-local recommendations. This shifts reactive decision-making to proactive readiness.

## 🌟 Project Overview

HealthEase is an Agentic AI system designed to optimize hospital operations through three interrelated phases:
1.  **Predictive Alert Phase**: Applies deep learning to accurately predict spikes in demand.
2.  **Proactive Preparation Phase**: Employs autonomous AI agents to instantaneously compute and implement best resource re-allocations.
3.  **Dynamic Response & Optimization Phase**: Offers real-time command center assistance to dynamically respond to emerging events.

The system is built with:
- **Python FastAPI Backend** - Modern async REST API
- **React + Vite Frontend** - Fast, responsive UI
- **MongoDB Database** - Flexible NoSQL storage with geospatial support
- **AI Integration** - OpenAI-powered surge predictions
- **Payment Processing** - Razorpay integration for referrals
- **Workflow Automation** - n8n workflows for alerts and automation

## 🏗️ Architecture

```
HealthEase/
├── backend/          # Python FastAPI + MongoDB
│   ├── app/
│   │   ├── models/      # 12 MongoDB collections
│   │   ├── routes/      # 25+ API endpoints
│   │   ├── services/    # AI, Wallet, Payment services
│   │   └── middleware/  # JWT auth & RBAC
│   └── requirements.txt
│
├── frontend/         # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── pages/       # Hospital/Patient/Admin UIs
│   │   ├── components/  # Reusable UI components
│   │   ├── store/       # Zustand state management
│   │   └── lib/         # API client & utilities
│   └── package.json
│
└── n8n-workflows/    # Automation workflows
```

## ✨ Key Features

### For Hospitals
- ⚡ **AI Surge Predictions** - Predict patient influx using weather, festivals, pollution data
- 📦 **Smart Inventory** - Auto-reorder during festival seasons (paid tier)
- 💰 **Digital Wallet** - Track referral earnings and request payouts
- 🏥 **Referral Management** - Accept/reject incoming patient referrals
- 📊 **Real-time Analytics** - Bed occupancy, ICU, ventilator tracking

### For Patients
- 🔍 **Hospital Search** - Find nearby hospitals with load probability
- ⏱️ **Wait Time Estimates** - Real-time capacity-based predictions
- 💸 **Smart Referrals** - ₹150 payment automatically distributed
- 🔔 **Health Alerts** - Pollution, epidemic, festival warnings
- 📱 **Android Compatible** - REST API works with mobile apps

### For Admins
- 📈 **System Analytics** - Hospitals, patients, revenue metrics
- 🏢 **Hospital Management** - Subscription upgrades/downgrades
- 💳 **Payout Processing** - Approve wallet withdrawals
- 📢 **Advertisement System** - Manage ads for free-tier hospitals
- 📝 **Workflow Monitoring** - Track n8n automation logs

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+ (or MongoDB Atlas account)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB, OpenAI, Razorpay credentials

# Run server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with API URL

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🔑 Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb://localhost:27017/healthease
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-your-key
RAZORPAY_KEY_ID=rzp_test_your_id
RAZORPAY_KEY_SECRET=your_secret
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 📊 Database Collections

1. **users** - Authentication with role-based access
2. **hospitals** - Hospital profiles with geospatial data
3. **patients** - Patient profiles with medical history
4. **inventory** - Stock management with low-stock alerts
5. **surge_predictions** - AI-generated predictions
6. **referrals** - Patient referral tracking
7. **wallets** - Hospital digital wallets
8. **wallet_transactions** - Transaction logs
9. **advertisements** - Hospital promotion system
10. **capacity_logs** - Time-series capacity tracking
11. **subscription_plans** - Free/Paid tier definitions
12. **workflow_logs** - n8n automation logs

## 🎨 UI Themes

The platform uses distinct color themes for each role:

- **Hospital**: Medical Blue (#1C6DD0) + Teal (#00B8A9)
- **Patient**: Soft Purple (#6C63FF) + Sky Blue (#48CAE4)
- **Admin**: Deep Navy (#14213D) + Gold (#FCA311)

## 💳 Payment Flow

1. Patient searches for hospitals → selects Hospital B
2. Hospital A (full capacity) creates referral to Hospital B
3. Patient pays ₹150 via Razorpay
4. **Distribution**:
   - ₹40 → Platform fee
   - ₹110 → Split between hospitals (AI-calculated)
5. Wallets credited immediately upon payment confirmation

## 🤖 AI Features

### Surge Prediction
Uses OpenAI to analyze:
- Historical hospital data
- Weather forecasts
- Festival calendar
- Pollution index (AQI)
- Local events

### Dynamic Pricing
AI calculates fair revenue split between hospitals based on:
- Current occupancy levels
- Distance between hospitals
- Specialization match

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - JWT login
- `GET /api/auth/me` - Current user

### Hospitals
- `GET /api/hospitals` - List hospitals
- `GET /api/hospitals/nearby?lat=19.07&lng=72.87&radius_km=10` - Geo search
- `PUT /api/hospitals/{id}/capacity` - Update capacity
- `GET /api/hospitals/{id}/surge-predictions` - AI predictions
- `GET /api/hospitals/{id}/wallet` - Wallet details

### Patients
- `GET /api/patients/hospitals/search` - Search with load probability
- `POST /api/patients/referrals` - Create referral + Razorpay order
- `POST /api/patients/referrals/{id}/payment` - Confirm payment

### Admin
- `GET /api/admin/analytics` - System metrics
- `POST /api/admin/payouts/{hospital_id}` - Process withdrawal
- `POST /api/admin/advertisements` - Manage ads

Full API docs: http://localhost:8000/docs

## 🔐 Security

- JWT-based authentication with RS256
- Role-based access control (RBAC)
- Razorpay signature verification for payments
- MongoDB indexes for query optimization
- CORS configured for production domains

## 📦 Deployment

### Backend (Render/Railway recommended)
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Database
- **Development**: Local MongoDB
- **Production**: MongoDB Atlas (free tier available)

## 🤝 Project Status

✅ **Backend**: 100% Complete
- All 12 MongoDB models
- All 25+ API endpoints
- AI service integration
- Payment processing
- Wallet management
- JWT authentication

✅ **Frontend**: Foundation Complete
- Routing with protected routes
- Authentication flow
- UI component library
- Landing page with features/pricing
- Login/Registration pages
- Themed design system

🚧 **In Progress**:
- Individual dashboard pages (Hospital/Patient/Admin)
- Payment integration UI
- Charts and analytics visualizations
- n8n workflow JSON files

## 🛠️ Technology Stack

**Backend**:
- FastAPI 0.104
- MongoDB 6.0+ with Beanie ODM
- OpenAI GPT-3.5
- Razorpay SDK
- Python-JOSE for JWT

**Frontend**:
- React 18
- Vite 5
- TailwindCSS 3
- Zustand (state)
- Axios
- React Router 6
- Lucide Icons

## 📝 License

Proprietary - All Rights Reserved

## 👥 Support

For issues or questions, contact: [your-email@example.com]

---

**HealthEase** - Transforming Healthcare with AI 🏥✨
