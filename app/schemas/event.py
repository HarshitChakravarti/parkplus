from pydantic import BaseModel, field_validator
import re
from datetime import datetime

class ANPREventCreate(BaseModel):
    plate: str
    floor: int | None = None
    checkpoint: str
    timestamp: datetime

    @field_validator("plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9]{4,15}$", v):
            raise ValueError("Invalid plate format")
        return v

    @field_validator("checkpoint")
    @classmethod
    def validate_checkpoint(cls, v: str) -> str:
        v = v.strip().upper()
        allowed_prefixes = ("F", "ENTRY", "EXIT", "GATE")
        if not any(v.startswith(p) for p in allowed_prefixes):
            raise ValueError("Unrecognized checkpoint format")
        return v


class ANPREventResponse(BaseModel):
    message: str
    plate: str
    checkpoint: str
    checkpoint_type: str | None = None
    status: str | None = None
    floor: int | None = None
