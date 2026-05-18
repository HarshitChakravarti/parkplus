from pydantic import BaseModel, field_validator
from datetime import datetime
import re

class VehicleRegisterRequest(BaseModel):
    plate_number: str
    owner_phone: str
    vehicle_type: str | None = None

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("owner_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^\+?[1-9]\d{7,14}$", v):
            raise ValueError("Invalid phone number format")
        return v


class VehicleRegisterResponse(BaseModel):
    message: str
    plate_number: str
    is_registered: bool


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
