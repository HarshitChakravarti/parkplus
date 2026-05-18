from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class VehicleEvent(Base):
    __tablename__ = "vehicle_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String, nullable=False, index=True)
    floor = Column(Integer, nullable=True)
    checkpoint = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
