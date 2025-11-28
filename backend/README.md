# HealthEase Backend - Python FastAPI

Production-grade backend for the Agentic AI Hospital Management & Patient Flow Platform.

## Features

- **FastAPI** - Modern, fast Python web framework
- **MongoDB** - NoSQL database with Beanie ODM
- **JWT Authentication** - Secure token-based auth with role-based access
- **Razorpay Integration** - Payment processing for referrals
- **OpenAI Integration** - AI-powered surge predictions and dynamic pricing
- **Digital Wallet System** - Platform-managed hospital wallets
- **Geospatial Queries** - Find nearby hospitals using MongoDB 2dsphere index

## Prerequisites

- Python 3.11+
- MongoDB 6.0+ (local or MongoDB Atlas)

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Update environment variables:
   - MongoDB connection string
   - JWT secret key
   - OpenAI API key
   - Razorpay credentials
   - SMTP settings

## Running the Server

### Development

```bash
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Hospitals
- `GET /api/hospitals` - List hospitals
- `GET /api/hospitals/nearby` - Find nearby hospitals (geospatial)
- `GET /api/hospitals/{id}` - Get hospital details
- `PUT /api/hospitals/{id}/capacity` - Update capacity
- `GET /api/hospitals/{id}/surge-predictions` - AI predictions
- `GET /api/hospitals/{id}/inventory` - Inventory management
- `GET /api/hospitals/{id}/referrals` - Referral management
- `GET /api/hospitals/{id}/wallet` - Wallet & transactions

### Patients
- `GET /api/patients/me` - Get patient profile
- `GET /api/patients/hospitals/search` - Search hospitals
- `POST /api/patients/referrals` - Create referral
- `POST /api/patients/referrals/{id}/payment` - Confirm payment
- `GET /api/patients/alerts` - Health alerts

### Admin
- `GET /api/admin/hospitals` - Manage hospitals
- `GET /api/admin/analytics` - System analytics
- `POST /api/admin/advertisements` - Manage ads
- `POST /api/admin/payouts/{id}` - Process payouts
- `GET /api/admin/n8n-logs` - Workflow logs

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings & environment
│   ├── database.py          # MongoDB connection
│   ├── models/              # Beanie ODM models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── middleware/          # Auth middleware
│   ├── utils/               # Helper functions
│   └── schemas/             # Pydantic schemas
├── requirements.txt         # Dependencies
└── .env.example            # Environment template
```

## MongoDB Collections

- `users` - User authentication
- `hospitals` - Hospital profiles with geospatial data
- `patients` - Patient profiles
- `inventory` - Hospital inventory
- `surge_predictions` - AI predictions
- `referrals` - Patient referrals
- `wallets` - Hospital digital wallets
- `wallet_transactions` - Transaction logs
- `advertisements` - Hospital ads
- `capacity_logs` - Time-series capacity tracking

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Deployment

See main README.md for deployment instructions.

## License

Proprietary
