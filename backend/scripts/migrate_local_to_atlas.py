"""
Local MongoDB to MongoDB Atlas Ingestion & Migration Script
This script reads all sessions, user records, and checkpoints from local MongoDB
(mongodb://localhost:27017/devils_advocate) and syncs them directly into production MongoDB Atlas.

Usage:
    python backend/scripts/migrate_local_to_atlas.py
"""

import sys
import os
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import settings

LOCAL_URI = "mongodb://localhost:27017"
ATLAS_URI = settings.effective_mongodb_uri
DB_NAME = settings.MONGODB_DB_NAME

async def migrate_data():
    print("=" * 65)
    print("[*] DEVIL'S ADVOCATE - LOCAL TO ATLAS INGESTION")
    print("=" * 65)
    print(f"Source (Local):  {LOCAL_URI} -> db: {DB_NAME}")
    
    # Mask Atlas URI password for safe printing
    masked_atlas = ATLAS_URI
    if "@" in ATLAS_URI:
        parts = ATLAS_URI.split("@")
        prefix = parts[0].split("://")[0]
        masked_atlas = f"{prefix}://****:****@{parts[1]}"
    print(f"Target (Atlas):  {masked_atlas} -> db: {DB_NAME}\n")

    local_client = None
    atlas_client = None

    try:
        local_client = AsyncIOMotorClient(LOCAL_URI, serverSelectionTimeoutMS=3000)
        atlas_client = AsyncIOMotorClient(ATLAS_URI, serverSelectionTimeoutMS=7000)

        # Ping both
        print("[*] Connecting to Local MongoDB...")
        await local_client.admin.command("ping")
        print("[+] Local MongoDB connected.")

        print("[*] Connecting to MongoDB Atlas...")
        await atlas_client.admin.command("ping")
        print("[+] MongoDB Atlas connected.\n")

        local_db = local_client[DB_NAME]
        atlas_db = atlas_client[DB_NAME]

        # Collections to migrate
        collections = ["sessions", "users", "checkpoints", "checkpoint_writes"]

        total_migrated = 0

        for col_name in collections:
            local_col = local_db[col_name]
            atlas_col = atlas_db[col_name]

            count = await local_col.count_documents({})
            print(f"[*] Collection '{col_name}': Found {count} documents locally.")

            if count == 0:
                continue

            cursor = local_col.find({})
            col_migrated = 0

            async for doc in cursor:
                # Use session_id or _id as unique key for upsert
                if "session_id" in doc:
                    await atlas_col.replace_one({"session_id": doc["session_id"]}, doc, upsert=True)
                elif "user_id" in doc:
                    await atlas_col.replace_one({"user_id": doc["user_id"]}, doc, upsert=True)
                elif "_id" in doc:
                    await atlas_col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
                col_migrated += 1

            # Ensure indexes in Atlas
            if col_name == "sessions":
                await atlas_col.create_index("session_id", unique=True)
                await atlas_col.create_index("user_id")
                await atlas_col.create_index("created_at")
            elif col_name == "users":
                await atlas_col.create_index("user_id", unique=True)
                await atlas_col.create_index("email")

            print(f"[+] Migrated {col_migrated} documents to Atlas '{col_name}' collection.")
            total_migrated += col_migrated

        print("\n" + "=" * 65)
        print(f"[+] INGESTION COMPLETE! Successfully synced {total_migrated} records to Atlas.")
        print(f"[+] Check MongoDB Compass under database: '{DB_NAME}' -> 'sessions'.")
        print("=" * 65)

    except Exception as e:
        print(f"[!] Migration error: {e}")
    finally:
        if local_client:
            local_client.close()
        if atlas_client:
            atlas_client.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
