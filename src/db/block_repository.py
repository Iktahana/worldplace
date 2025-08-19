"""Block Repository Module
This module provides database operations for Block entities.
"""
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.db.mongodb import get_database
from src.model.block import BlockInDB, BlockMetadata

# Collection name
BLOCK_COLLECTION = "blocks"


class BlockRepository:
    """Repository for Block operations"""

    def __init__(self, database: AsyncIOMotorDatabase = None):
        self.database = database

    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.database is None:
            self.database = await get_database()
        return self.database

    async def _get_collection(self):
        """Get blocks collection"""
        db = await self._get_db()
        return db[BLOCK_COLLECTION]

    async def create_block(self, block: BlockInDB) -> BlockInDB:
        """Create a new block in the database

        Args:
            block: BlockInDB object to create

        Returns:
            BlockInDB: Created block
        """
        collection = await self._get_collection()

        # Convert to dict for MongoDB
        block_dict = block.model_dump()

        # Create a compound index on ix and iy to ensure uniqueness
        await collection.create_index([("ix", 1), ("iy", 1)], unique=True)

        # Insert the document
        await collection.insert_one(block_dict)

        return block

    async def get_block(self, ix: int, iy: int) -> Optional[BlockInDB]:
        """Get a block by coordinates

        Args:
            ix: X coordinate index
            iy: Y coordinate index

        Returns:
            Optional[BlockInDB]: Found block or None
        """
        collection = await self._get_collection()
        block_dict = await collection.find_one({"ix": ix, "iy": iy})

        if block_dict is None:
            return None

        # Convert MongoDB _id to string and remove it
        block_dict["_id"] = str(block_dict["_id"])

        # Handle metadata if it exists
        if block_dict.get("metadata"):
            metadata = BlockMetadata(**block_dict["metadata"])
            block_dict["metadata"] = metadata

        return BlockInDB(**block_dict)

    async def update_block_metadata(self, ix: int, iy: int, metadata: BlockMetadata) -> Optional[BlockInDB]:
        """Update block metadata

        Args:
            ix: X coordinate index
            iy: Y coordinate index
            metadata: New metadata

        Returns:
            Optional[BlockInDB]: Updated block or None if not found
        """
        collection = await self._get_collection()

        # Convert metadata to dict
        metadata_dict = metadata.model_dump()

        result = await collection.update_one(
            {"ix": ix, "iy": iy},
            {"$set": {"metadata": metadata_dict}}
        )

        if result.matched_count == 0:
            return None

        return await self.get_block(ix, iy)

    async def get_blocks_in_area(self, min_ix: int, min_iy: int, max_ix: int, max_iy: int) -> List[BlockInDB]:
        """Get blocks in a specified area

        Args:
            min_ix: Minimum X coordinate index
            min_iy: Minimum Y coordinate index
            max_ix: Maximum X coordinate index
            max_iy: Maximum Y coordinate index

        Returns:
            List[BlockInDB]: List of blocks in the area
        """
        collection = await self._get_collection()

        # Query blocks within the specified area
        cursor = collection.find({
            "ix": {"$gte": min_ix, "$lte": max_ix},
            "iy": {"$gte": min_iy, "$lte": max_iy}
        })

        blocks = []
        async for block_dict in cursor:
            # Convert MongoDB _id to string
            block_dict["_id"] = str(block_dict["_id"])

            # Handle metadata if it exists
            if block_dict.get("metadata"):
                metadata = BlockMetadata(**block_dict["metadata"])
                block_dict["metadata"] = metadata

            blocks.append(BlockInDB(**block_dict))

        return blocks
