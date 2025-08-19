"""
Block model
"""
from datetime import datetime, timezone
from typing import *

from pydantic import *


class BlockMetadata(BaseModel):
    author: Optional[str] = None
    author_ip: Optional[str] = None
    color: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "author": "demo_user",
                "author_ip": "192.168.1.1",
                "color": "#3498db"
            }
        }


class BlockInDB(BaseModel):
    ix: int
    iy: int
    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[BlockMetadata] = None


class BlockModel(BlockInDB):
    lon: Tuple[float, float]  # Source point
    lat: Tuple[float, float]  # Second point
    block_id: str
    visible_name_dd: str
    visible_name_dms: str
    metadata: Optional[Any] = None

    class Config:
        json_schema_extra = {
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
