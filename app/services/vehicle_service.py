from sqlalchemy.orm import Session
from app.models.vehicle_event import VehicleEvent
from app.models.vehicle_state import CurrentVehicleState
from app.models.vehicle import Vehicle
from app.redis_client import get_redis
from app.services.state_service import get_vehicle_state


def register_vehicle(db: Session, plate: str, owner_phone: str, vehicle_type: str | None) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()

    if vehicle:
        # Known plate — update with owner info
        vehicle.owner_phone = owner_phone
        vehicle.vehicle_type = vehicle_type
        vehicle.is_registered = True
    else:
        # New plate — create registered
        vehicle = Vehicle(
            plate_number=plate,
            owner_phone=owner_phone,
            vehicle_type=vehicle_type,
            is_registered=True,
        )
        db.add(vehicle)

    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_vehicle_detail(db: Session, plate: str) -> dict | None:
    r = get_redis()
    state = get_vehicle_state(r, plate, db)
    if not state:
        return None

    history = (
        db.query(VehicleEvent)
        .filter(VehicleEvent.plate_number == plate)
        .order_by(VehicleEvent.timestamp.desc())
        .limit(50)
        .all()
    )

    return {
        "plate": plate,
        "current_floor": state["current_floor"],
        "status": state["status"],
        "last_seen": state["last_seen"],
        "history": [
            {
                "floor": e.floor,
                "checkpoint": e.checkpoint,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in history
        ],
    }