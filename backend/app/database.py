from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    

db = Database()


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie ODM"""
    try:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        
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
        
        # Initialize Beanie with all document models
        await init_beanie(
            database=db.client.get_default_database(),
            document_models=[
                User,
                Hospital,
                Patient,
                Inventory,
                SurgePrediction,
                Referral,
                Wallet,
                WalletTransaction,
                SubscriptionPlan,
                Advertisement,
                CapacityLog,
                WorkflowLog
            ]
        )
        
        logger.info("Successfully connected to MongoDB and initialized Beanie")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    try:
        if db.client:
            db.client.close()
            logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
