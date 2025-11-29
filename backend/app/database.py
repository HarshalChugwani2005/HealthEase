from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging
import certifi

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    connected: bool = False
    

db = Database()


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie ODM"""
    from app.utils.mongo_utils import get_direct_connection_url
    
    # Import all models here to register with Beanie
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

    async def init_db(client):
        await init_beanie(
            database=client.get_default_database(),
            document_models=document_models
        )

    # 1. Try Standard Connection
    try:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
        # Use certifi CA bundle to avoid Windows trust store issues
        mongo_kwargs = {
            "serverSelectionTimeoutMS": 10000,
            "connectTimeoutMS": 10000,
        }
        # Base TLS settings
        if settings.mongodb_url.startswith("mongodb+srv://") or settings.mongodb_url.startswith("mongodb://"):
            if settings.mongodb_tls_insecure:
                mongo_kwargs.update({"tls": True, "tlsInsecure": True})
            else:
                mongo_kwargs.update({"tls": True, "tlsCAFile": certifi.where()})

        db.client = AsyncIOMotorClient(settings.mongodb_url, **mongo_kwargs)
        await init_db(db.client)
        db.connected = True
        logger.info("Successfully connected to MongoDB and initialized Beanie")
        return

    except Exception as e:
        logger.error(f"Standard MongoDB connection failed: {e}")
    
    # 2. Try Direct Fallback (if applicable)
    try:
        fallback_url = get_direct_connection_url(settings.mongodb_url)
        if fallback_url:
            logger.warning("Attempting direct MongoDB fallback...")
            # Direct fallback already includes tlsInsecure=true in the URL
            db.client = AsyncIOMotorClient(
                fallback_url,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
            )
            await init_db(db.client)
            db.connected = True
            logger.info("Successfully connected to MongoDB via direct fallback")
            return
    except Exception as e:
        logger.error(f"Direct MongoDB fallback failed: {e}")

    # 3. Try Localhost Fallback
    try:
        local_url = "mongodb://localhost:27017/healthease"
        logger.warning(f"Attempting local MongoDB fallback at {local_url}")
        db.client = AsyncIOMotorClient(
            local_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        await init_db(db.client)
        db.connected = True
        logger.info("Connected to local MongoDB and initialized Beanie")
    except Exception as fe:
        logger.error(f"Local MongoDB fallback failed: {fe}")
        db.connected = False
        # Do not raise here so the app can start in degraded mode
        return


async def close_mongo_connection():
    """Close MongoDB connection"""
    try:
        if db.client:
            db.client.close()
            logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
