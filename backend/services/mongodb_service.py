"""
MongoDB Persistence Service for AgriGenius.
Stores all module inputs, parameters, auto-retrieved signals, and agent outputs.
Reads MONGODB_URI from environment variables (.env file).
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()

_mongo_client = None
_db = None


def get_mongo_db():
    """
    Initialize and return MongoDB database instance.
    Returns None if MONGODB_URI is empty or connection fails.
    """
    global _mongo_client, _db
    if _db is not None:
        return _db

    if not MONGODB_URI or MONGODB_URI == "mongodb+srv://your_username:your_password@your_cluster.mongodb.net/agri_genius?retryWrites=true&w=majority":
        return None

    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        # Ping to check connection
        _mongo_client.admin.command('ping')
        _db = _mongo_client.get_database("agri_genius")
        print("[MongoDB] Connected successfully to agri_genius database.")
        return _db
    except Exception as e:
        print(f"[MongoDB] Connection warning (using local fallback storage): {e}")
        return None


def get_mongodb_status() -> Dict[str, Any]:
    """
    Check if MongoDB connection is active and configured.
    """
    db = get_mongo_db()
    if db is not None:
        return {
            "status": "connected",
            "database": "agri_genius",
            "message": "MongoDB active and recording module inputs/outputs."
        }
    return {
        "status": "unconfigured_or_offline",
        "database": None,
        "message": "MongoDB URI not set or offline. Saving records to local SQLite fallback."
    }


def save_record(collection_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any], module_name: str) -> bool:
    """
    Save module inputs and outputs into MongoDB collection.
    """
    db = get_mongo_db()
    document = {
        "module": module_name,
        "input_data": input_data,
        "output_data": output_data,
        "created_at": datetime.utcnow().isoformat(),
        "district": "Warangal, Telangana"
    }

    if db is not None:
        try:
            db[collection_name].insert_one(document)
            print(f"[MongoDB] Saved record to collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"[MongoDB] Failed to insert record into '{collection_name}': {e}")
            return False
    return False
