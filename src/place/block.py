"""
This file defines a latitude system based on latitude and longitude.
The minimum unit is 0.0001 degrees × 0.0001 degrees.
Take the upper left corner as the origin (0,0), and the longitude
 is increasing to the right and the latitude is increasing to the bottom.
Near the equator, each small square has a side length of about 11.132 meters
 and an area of about 124 square meters.
Since the earth is a sphere, the distance in the longitude direction
 will shrink with latitude, and the actual grid area will vary depending on location.

# Block number
 The coordinate number consists of 2 ints with a maximum of 5 digits, which is actually x10000 times the coordinate of the block origin (top left corner)
 For example
 (10000, 10000) means E1.0000, W1.0000
(1, 1) means E0.0001, W0.0001

The function "get_block" will return (y1, y2), (x1, x2) of the block
"""
import random
from datetime import datetime, timezone
from typing import List

from src import place
from src.db.block_repository import BlockRepository
from src.model.block import BlockModel, BlockMetadata, BlockInDB
from src.place.__init__ import *


def format_dd(lat: float, lon: float) -> str:
    """outputInDecimalDegreesFormat"""
    return f"Lat {lat:.4f}°, Lon {lon:.4f}°"


def format_dms(lat: float, lon: float) -> str:
    """outputInDegreesAndSecondsFormat"""

    def to_dms(value: float, is_lat: bool):
        deg = int(abs(value))
        minutes_full = (abs(value) - deg) * 60
        minutes = int(minutes_full)
        seconds = (minutes_full - minutes) * 60
        hemi = (
            "N" if (is_lat and value >= 0) else
            "S" if is_lat else
            "E" if value >= 0 else "W"
        )
        return f"{deg}°{minutes}′{seconds:.2f}″{hemi}"

    return f"{to_dms(lat, True)}, {to_dms(lon, False)}"


def to_block_id(ix: int, iy: int):
    """Convert block coordinates to a block ID string with fixed width

    Args:
        ix: X coordinate index
        iy: Y coordinate index

    Returns:
        str: Block ID in format "ix#iy" with fixed width digits
    """
    if not isinstance(ix, int) or not isinstance(iy, int):
        raise TypeError(f"ix and iy must be integers")
    # 動態計算需要的位數
    digits = len(str(place.__SCALE__))
    return f"{ix:0{digits}d}#{iy:0{digits}d}"


def to_block_index(block_id: str) -> (int, int):
    """Convert a block ID string to coordinates

    Args:
        block_id: Block ID in format "ix#iy"

    Returns:
        tuple: (ix, iy) coordinates
    """
    ix, iy = block_id.split("#")
    return int(ix), int(iy)


def _create_block_model(block_indb: BlockInDB) -> BlockModel:
    """
    根據數據庫中的塊模型創建完整的 BlockModel

    這是一個內部輔助函數，用於統一創建 BlockModel 的邏輯

    Args:
        block_indb: 數據庫中的塊模型

    Returns:
        BlockModel: 完整的塊模型，包含經緯度和顯示名稱
    """
    # 將 Pydantic 模型轉換為字典（如果尚未轉換）
    if not isinstance(block_indb, dict):
        block_data = block_indb.model_dump()
    else:
        block_data = block_indb

    ix = block_data['ix']
    iy = block_data['iy']

    # 計算經緯度範圍
    lon_min = index_to_coord(ix)
    lon_max = index_to_coord(ix + 1)
    lat_min = index_to_coord(iy)
    lat_max = index_to_coord(iy + 1)

    # 創建並返回 BlockModel
    return BlockModel(
        ix=ix,
        iy=iy,
        create_time=block_data.get('create_time', datetime.now(timezone.utc)),
        metadata=block_data['metadata'],
        lon=(lon_min, lon_max),
        lat=(lat_min, lat_max),
        block_id=to_block_id(ix, iy),
        visible_name_dd=format_dd(lat_min, lon_min),  # ← 這裡用小數度數格式
        visible_name_dms=format_dms(lat_min, lon_min),  # ← 這裡用度分秒格式
    )


async def get_block(block_id: str) -> BlockModel:
    """
    Get the block with the specified ID

    Calculate the corresponding latitude and longitude range and return the BlockModel

    Args:
            block_id: Block ID in the format "ix#iy"

    Returns:
            BlockModel: The block model
    """
    ix, iy = to_block_index(block_id)

    # 從數據庫查詢區塊
    block_indb = await BlockRepository().get_block(ix=ix, iy=iy)

    # 如果不存在，創建一個預設區塊
    if block_indb is None:
        block_indb = BlockInDB(ix=ix, iy=iy, metadata=None)

    # 使用共享邏輯創建 BlockModel
    return _create_block_model(block_indb)


async def get_blocks_in_range(min_ix: int, min_iy: int, max_ix: int, max_iy: int) -> List[BlockModel]:
    """
    Get all blocks within the specified area

    This is an optimized batch query method that fetches multiple blocks directly from the database, reducing network requests

    Args:
            min_ix: Minimum X coordinate index
            min_iy: Minimum Y-coordinate index
            max_ix: Maximum X-coordinate index
            max_iy: Maximum Y-coordinate index

    Returns:
            List[BlockModel]: A list of blocks in the region
    """
    blocks_in_db = await BlockRepository().get_blocks_in_area(min_ix, min_iy, max_ix, max_iy)
    blocks_dict = {(block.ix, block.iy): block for block in blocks_in_db}

    result = []

    for ix in range(min_ix, max_ix + 1):
        for iy in range(min_iy, max_iy + 1):
            block_indb = blocks_dict.get((ix, iy))

            if block_indb is None:
                block_indb = BlockInDB(ix=ix, iy=iy, metadata=None)

            result.append(_create_block_model(block_indb))

    return result


async def place_a_block(block_id: str, metadata: BlockMetadata):
    """Write metadata to a block and save to database

    Args:
        block_id: Block ID in format "ix#iy"
        metadata: Block metadata to save

    Returns:
        BlockModel: Updated block
    """
    ix, iy = to_block_index(block_id)

    block_indb = await BlockRepository().get_block(ix=ix, iy=iy)

    if block_indb is None:
        block_indb = BlockInDB(ix=ix, iy=iy, metadata=metadata)
        await BlockRepository().create_block(block_indb)
    else:
        await BlockRepository().update_block_metadata(ix, iy, metadata)

    # 使用更新的 get_block 方法
    return await get_block(block_id)


async def test_blocks():
    """Test function to demonstrate block operations"""
    print(
        await place_a_block(to_block_id(1, 1), BlockMetadata(author="test", color=f"#{random.randint(0, 0xFFFFFF):06x}"
                                                             ))
    )
    print(await get_block(to_block_id(1, 1)))


if __name__ == '__main__':
    import asyncio

    asyncio.run(test_blocks())
