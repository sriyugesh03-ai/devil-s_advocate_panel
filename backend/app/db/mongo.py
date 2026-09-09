from motor.motor_asyncio import AsyncIOMotorClient
import logging
from typing import Optional, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    connected: bool = False
    cluster_info: Optional[str] = None

db_instance = MongoDB()

async def connect_to_mongo():
    """Initializes production connection pool to MongoDB Atlas with ping validation and indexing."""
    try:
        uri = settings.effective_mongodb_uri
        if not uri:
            logger.warning("MongoDB URI is not configured. Falling back to in-memory storage.")
            db_instance.connected = False
            return

        # Sanitize URI for log output
        sanitized_uri = uri
        if "@" in uri:
            prefix = uri.split("@")[0]
            host_part = uri.split("@")[1]
            scheme = prefix.split("://")[0]
            sanitized_uri = f"{scheme}://****:****@{host_part}"

        logger.info(f"Connecting to MongoDB Atlas endpoint: {sanitized_uri}")

        db_instance.client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=2,
            retryWrites=True
        )
        
        # Ping the server to verify active connection
        await db_instance.client.admin.command('ping')
        
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        db_instance.connected = True
        db_instance.cluster_info = sanitized_uri

        # Ensure indexes for sessions and users
        await db_instance.db.sessions.create_index("session_id", unique=True)
        await db_instance.db.sessions.create_index("user_id")
        await db_instance.db.sessions.create_index("created_at")
        await db_instance.db.users.create_index("user_id", unique=True)
        await db_instance.db.users.create_index("email")

        logger.info(f"Successfully connected to MongoDB Atlas database '{settings.MONGODB_DB_NAME}' with indexes configured.")
    except Exception as e:
        db_instance.connected = False
        db_instance.db = None
        logger.warning(f"MongoDB Atlas connection unestablished ({e}). Falling back to in-memory session cache.")

async def close_mongo_connection():
    """Closes MongoDB connection pool gracefully."""
    if db_instance.client:
        db_instance.client.close()
        db_instance.connected = False
        db_instance.client = None
        db_instance.db = None
        logger.info("Closed MongoDB Atlas connection.")

def get_db():
    """Returns active database handle if connected, else None."""
    return db_instance.db

def is_connected() -> bool:
    """Returns whether live MongoDB connection is active."""
    return db_instance.connected and db_instance.db is not None

def get_db_status() -> Dict[str, Any]:
    """Returns sanitized MongoDB Atlas status dictionary for health endpoints."""
    return {
        "connected": is_connected(),
        "database": settings.MONGODB_DB_NAME if is_connected() else None,
        "endpoint": db_instance.cluster_info if is_connected() else "fallback_in_memory"
    }

