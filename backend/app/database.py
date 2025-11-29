"""
MongoDB database connection and initialization module.
Handles connection to MongoDB Atlas with automatic fallback mechanisms.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    client: AsyncIOMotorClient = None
    connected: bool = False


db = Database()


async def connect_to_mongo():
    """
    Connect to MongoDB and initialize Beanie ODM.
    Supports MongoDB Atlas with srv:// protocol.
    """
    
    # Import all models for Beanie registration
    from app.models.user import User
    from app.models.hospital import Hospital
    from app.models.patient import Patient
    from app.models.inventory import Inventory
    from app.models.surge_prediction import SurgePrediction
    from app.models.referral import Referral
    from app.models.wallet import Wallet, WalletTransaction
    from app.models.subscription import SubscriptionPlan
    from app.models.advertisement import Advertisement
    from app.models.capacity_log import CapacityLog
    from app.models.workflow_log import WorkflowLog
    from app.models.review import Review
    from app.models.notification import Notification
    from app.models.appointment import Appointment
    from app.models.medication import Medication, MedicationReminder, Prescription
    from app.models.analytics import Analytics, HealthAlert, PatientOutcome
    from app.models.telemedicine import IoTDevice, HealthData, TelemedicineSession, EmergencyAlert
    from app.models.workflow import N8NWorkflow, WorkflowExecution, WorkflowTemplate, AutomationRule

    document_models = [
        User, Hospital, Patient, Inventory, SurgePrediction, Referral,
        Wallet, WalletTransaction, SubscriptionPlan, Advertisement,
        CapacityLog, WorkflowLog, Review, Notification, Appointment,
        Medication, MedicationReminder, Prescription, Analytics,
        HealthAlert, PatientOutcome, IoTDevice, HealthData, TelemedicineSession,
        EmergencyAlert, N8NWorkflow, WorkflowExecution, WorkflowTemplate, AutomationRule
    ]

    try:
        logger.info(f"Connecting to MongoDB...")
        
        # Create MongoDB client with SSL/TLS disabled
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Initialize Beanie with all document models
        await init_beanie(
            database=db.client.get_default_database(),
            document_models=document_models
        )
        
        # Test the connection
        await db.client.admin.command('ping')
        
        db.connected = True
        logger.info("✓ Successfully connected to MongoDB and initialized Beanie")
        
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        db.connected = False
        logger.warning("⚠ Application starting in DEGRADED MODE (Database unavailable)")


async def close_mongo_connection():
    """Close MongoDB connection gracefully"""
    try:
        if db.client:
            db.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
