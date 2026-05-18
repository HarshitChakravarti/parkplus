from sqlalchemy.orm import Session
import logging
from app.models.vehicle import Vehicle
from app.models.vehicle_event import VehicleEvent
from app.models.vehicle_state import CurrentVehicleState
from app.schemas.event import ANPREventCreate
from app.services.state_service import set_vehicle_state
from app.services.notification_service import notify_if_needed
from app.redis_client import get_redis

logger = logging.getLogger(__name__)


def determine_status(checkpoint: str) -> str:
    """Derive vehicle status from checkpoint string."""
    cp = checkpoint.upper()
    if "EXIT" in cp or cp == "GATE_OUT":
        return "exited"
    return "inside"


def process_anpr_event(db: Session, event: ANPREventCreate) -> dict:
    plate = event.plate
    status = determine_status(event.checkpoint)

    # 1. Auto-register vehicle if not known
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(plate_number=plate)
        db.add(vehicle)
        db.flush()  # get the ID without committing yet

    # 2. Log the event permanently
    new_event = VehicleEvent(
        plate_number=plate,
        floor=event.floor,
        checkpoint=event.checkpoint,
        timestamp=event.timestamp,
    )
    db.add(new_event)

    # Capture previous state BEFORE overwriting it
    previous_state = db.query(CurrentVehicleState).filter(
        CurrentVehicleState.plate_number == plate
    ).first()

    # Take a snapshot of values before the upsert mutates the object
    prev_snapshot = None
    if previous_state:
        from dataclasses import dataclass
        @dataclass
        class Snapshot:
            current_floor: int | None
            status: str
        prev_snapshot = Snapshot(
            current_floor=previous_state.current_floor,
            status=previous_state.status,
        )

    # 3. Upsert current state
    if previous_state:
        previous_state.current_floor = event.floor
        previous_state.last_seen = event.timestamp
        previous_state.status = status
    else:
        previous_state = CurrentVehicleState(
            plate_number=plate,
            current_floor=event.floor,
            last_seen=event.timestamp,
            status=status,
        )
        db.add(previous_state)

    # 4. Commit everything atomically
    db.commit()

    # Write to Redis after successful Postgres commit
    try:
        r = get_redis()
        set_vehicle_state(r, plate, event.floor, status, event.timestamp)
    except Exception as redis_err:
        logger.warning(f"Redis write failed for {plate}, state only in Postgres: {redis_err}")

    # Notify after commit — failure here never rolls back the event
    notify_if_needed(db, plate, event.floor, status, prev_snapshot)

    return {
        "plate": plate,
        "checkpoint": event.checkpoint,
        "status": status,
        "floor": event.floor,
        "timestamp": event.timestamp.isoformat(),
    }
