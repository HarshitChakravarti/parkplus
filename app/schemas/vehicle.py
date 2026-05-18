from pydantic import BaseModel
from datetime import datetime


class VehicleStateResponse(BaseModel):
    plate: str
    current_floor: int | None
    status: str
    last_seen: datetime

    class Config:
        from_attributes = True


class EventHistoryResponse(BaseModel):
    plate_number: str
    floor: int | None
    checkpoint: str
    timestamp: datetime

    class Config:
        from_attributes = True


class FloorOccupancy(BaseModel):
    floor: int
    count: int


class OccupancyResponse(BaseModel):
    total_inside: int
    by_floor: list[FloorOccupancy]
