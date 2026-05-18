from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String, unique=True, nullable=False, index=True)
    owner_phone = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
