from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CurrentVehicleState(Base):
    __tablename__ = "current_vehicle_state"

    plate_number = Column(String, primary_key=True, index=True)
    current_floor = Column(Integer, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="inside")  # "inside" | "exited"
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
