"""
For draw API
"""
from typing import *

from fastapi import APIRouter, HTTPException, Query, Body

from src import place
from src.api import __BLOCKS_IN_RANGE_MAXIMUM__
from src.model.block import BlockModel
from src.place import block

router = APIRouter(
    tags=["Block"],
    prefix="/block",
)


@router.get("/get", response_model=block.BlockModel,
            description=f"Get a block with *index coordinate*(✖{place.__SCALE__}) e.g. when The latitude and longitude are [{place.__STEP__},{place.__STEP__}], you need input [{place.coord_to_index(place.__STEP__)},{place.coord_to_index(place.__STEP__)}]. ")
async def get_a_block(block_id: str):
    """
    Get a block with index coordinate
     e.g. [1, 1]
    """
    return await place.block.get_block(block_id)


@router.get("/range", response_model=List[block.BlockModel],
            responses={
                413: {
                    "description": f"The scope of the request is too large. The area cannot exceed a certain size limit.(>={__BLOCKS_IN_RANGE_MAXIMUM__})。",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "If the search range is too large, please narrow down the search area.(>={__BLOCKS_IN_RANGE_MAXIMUM__})"}
                        }
                    }
                }
            })
async def get_blocks_in_range(
        x1: float = Query(0.0001, description="The upper latitude limit, for example: 0.0001"),
        y1: float = Query(0.0001, description="The upper latitude limit, for example: 0.0001"),
        x2: float = Query(0.0005, description="The upper latitude limit, for example: 0.0005"),
        y2: float = Query(0.0005, description="The upper latitude limit, for example: 0.0005")):
    """
    Return all blocks within a square coordinate range.

    Each coordinate represents a 0.0001° × 0.0001° area on Earth.
    Near the equator, each block is approximately 11.132 meters on each side (about 124 square meters).

    Example query: /block/range?x1=0.0001&y1=0.0001&x2=0.0002&y2=0.0002

    Args:
        x1: Minimum longitude (west boundary), e.g. 0.0001
        y1: Minimum latitude (south boundary), e.g. 0.0001
        x2: Maximum longitude (east boundary), e.g. 0.0002
        y2: Maximum latitude (north boundary), e.g. 0.0002
    Returns:
        List[BlockModel]: List of blocks in the specified area
    """
    # Limit traffic
    if (x2 - x1 + 1) * (y2 - y1 + 1) >= __BLOCKS_IN_RANGE_MAXIMUM__:
        raise HTTPException(413, "Too many blocks requested, narrow the range")

    # sort
    lon_min, lon_max = sorted([x1, x2])
    lat_min, lat_max = sorted([y1, y2])

    # convert to block index
    ix1 = place.coord_to_index(lon_min)
    ix2 = place.coord_to_index(lon_max)
    iy1 = place.coord_to_index(lat_min)
    iy2 = place.coord_to_index(lat_max)

    return await block.get_blocks_in_range(ix1, iy1, ix2, iy2)


@router.post("/place", response_model=block.BlockModel,
             responses={
                 200: {
                     "description": "Place or update a block successfully.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "ix": 1,
                                 "iy": 1,
                                 "create_time": "2025-08-19T08:30:00.000Z",
                                 "metadata": {
                                     "author": "demo_user",
                                     "author_ip": "192.168.1.1",
                                     "color": "#3498db"
                                 },
                                 "lon": [0.0001, 0.0002],
                                 "lat": [0.0001, 0.0002],
                                 "block_id": "00001#00001",
                                 "visible_name_dd": "Lat 0.0001°, Lon 0.0001°",
                                 "visible_name_dms": "0°0′0.36″N, 0°0′0.36″E"
                             }
                         }
                     }
                 }
             })
async def place_a_block(
        block_id: str = Query(..., description="Block ID 'ix#iy', e.g.'00001#00001'"),
        metadata: block.BlockMetadata = Body(...,
                                             description="Block metadata, which must be sent by requesting the body of the JSON."),
):
    """
    Place or update a block

    Add metadata (author, color, etc.) to the specified block and save it to the database

    Args:
            block_id: Block ID, format 'ix#iy'
            metadata: The block metadata, which must be sent by requesting the body of the JSON

    Returns:
            BlockModel: The updated block
    """
    return await place.block.place_a_block(block_id, metadata)
