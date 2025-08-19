"""MongoDB Connection Module
This module provides functionality to connect to MongoDB database.
"""
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

# MongoDB connection singleton
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

# Default configuration
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://mongodb:27017")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "place_db")


async def connect_to_mongodb() -> AsyncIOMotorDatabase:
    """Connect to MongoDB and return database instance
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    global _client, _db

    if _db is not None:
        return _db

    try:
        _client = AsyncIOMotorClient(MONGODB_URI)
        # Ping the server to confirm connection
        await _client.admin.command('ping')
        print("Successfully connected to MongoDB")

        _db = _client[DATABASE_NAME]
        return _db
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    if _db is None:
        return await connect_to_mongodb()
    return _db


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global _client
    if _client is not None:
        _client.close()
        print("MongoDB connection closed")
