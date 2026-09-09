from motor.motor_asyncio import AsyncIOMotorClient
import logging
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URI}, db: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Fallback to in-memory caching if needed.")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("Closed MongoDB connection.")

def get_db():
    return db_instance.db
