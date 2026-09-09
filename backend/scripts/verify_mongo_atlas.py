"""
MongoDB Atlas Connection & Schema Verification Script
Run this script to verify connectivity to your MongoDB Atlas cluster, check indexes,
and test document persistence under production conditions.

Usage:
    python backend/scripts/verify_mongo_atlas.py
"""

import sys
import os
import asyncio
from pathlib import Path
import datetime

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import settings
from backend.app.db.mongo import connect_to_mongo, close_mongo_connection, get_db, is_connected, get_db_status

async def run_verification():
    print("=" * 65)
    print("[*] DEVIL'S ADVOCATE PANEL - MONGODB ATLAS VERIFICATION")
    print("=" * 65)
    print(f"Configured Database Name: {settings.MONGODB_DB_NAME}")
    
    uri = settings.effective_mongodb_uri
    if not uri:
        print("[!] Error: Neither MONGODB_URI nor MONGO_DB_URL is defined.")
        return False

    # Sanitize URI for safe display
    sanitized_uri = uri
    if "@" in uri:
        scheme = uri.split("://")[0]
        host = uri.split("@")[1]
        sanitized_uri = f"{scheme}://****:****@{host}"
    print(f"Connecting to URI: {sanitized_uri}")

    try:
        await connect_to_mongo()
        
        if not is_connected():
            print("[!] Failed to connect to MongoDB Atlas cluster (running in offline/in-memory fallback mode).")
            return False

        db = get_db()
        print("[+] Connection established successfully!")
        
        # Check Indexes on collections
        print("\n--- 1. Checking Collection Indexes ---")
        session_indexes = await db.sessions.index_information()
        print(f"  * 'sessions' collection indexes: {list(session_indexes.keys())}")
        
        user_indexes = await db.users.index_information()
        print(f"  * 'users' collection indexes: {list(user_indexes.keys())}")

        # Test write & read roundtrip
        print("\n--- 2. Testing Write & Read Operations ---")
        test_session_id = f"test_verify_{int(datetime.datetime.now().timestamp())}"
        test_doc = {
            "session_id": test_session_id,
            "user_id": "usr_test_verification",
            "status": "TESTING",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "pitch": {
                "startup_name": "Atlas Test Venture",
                "one_liner": "Testing production MongoDB Atlas persistence."
            }
        }

        # Insert
        insert_res = await db.sessions.insert_one(test_doc)
        print(f"[+] Inserted test document with ID: {insert_res.inserted_id}")

        # Fetch
        fetched = await db.sessions.find_one({"session_id": test_session_id})
        assert fetched is not None, "Failed to retrieve test document!"
        print(f"[+] Retrieved test document: {fetched['pitch']['startup_name']} (session: {fetched['session_id']})")

        # Cleanup
        del_res = await db.sessions.delete_one({"session_id": test_session_id})
        print(f"[+] Cleaned up test document ({del_res.deleted_count} removed)")

        print("\n" + "=" * 65)
        print("[+] MONGODB ATLAS PRODUCTION INTEGRATION VERIFIED SUCCESSFULLY!")
        print("=" * 65)
        return True

    except Exception as e:
        print(f"[!] Verification failed with error: {e}")
        return False
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    success = asyncio.run(run_verification())
    sys.exit(0 if success else 1)
