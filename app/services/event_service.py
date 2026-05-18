from sqlalchemy.orm import Session
import logging
from app.models.vehicle import Vehicle
from app.models.vehicle_event import VehicleEvent
from app.models.vehicle_state import CurrentVehicleState
from app.schemas.event import ANPREventCreate
from app.services.state_service import set_vehicle_state
from app.services.notification_service import notify_if_needed
from app.redis_client import get_redis
from app.services.checkpoint_service import classify_checkpoint, derive_vehicle_status, resolve_state_floor

logger = logging.getLogger(__name__)

def process_anpr_event(db: Session, event: ANPREventCreate) -> dict:
    plate = event.plate

    # Classify the checkpoint
    cp_info = classify_checkpoint(event.checkpoint)
    cp_type = cp_info["type"]
    status = derive_vehicle_status(cp_type)

    # Use floor from classifier if event floor is missing
    event_floor = event.floor if event.floor is not None else cp_info["floor"]
    state_floor = resolve_state_floor(cp_type, event_floor)

    # Auto-register as unregistered if plate is unknown
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(plate_number=plate, is_registered=False)
        db.add(vehicle)
        db.flush()

    # Log event permanently
    new_event = VehicleEvent(
        plate_number=plate,
        floor=event_floor,
        checkpoint=event.checkpoint,
        timestamp=event.timestamp,
    )
    db.add(new_event)

    # Capture previous state before overwriting
    prev_floor = None
    prev_status = None
    state = db.query(CurrentVehicleState).filter(
        CurrentVehicleState.plate_number == plate
    ).first()
    if state:
        state.current_floor = state_floor
        state.last_seen = event.timestamp
        state.status = status
    else:
        state = CurrentVehicleState(
            plate_number=plate,
            current_floor=state_floor,
            last_seen=event.timestamp,
            status=status,
        )
        db.add(state)

    db.commit()

    # Update Redis
    try:
        r = get_redis()
        set_vehicle_state(r, plate, state_floor, status, event.timestamp)
    except Exception as redis_err:
        logger.warning(f"Redis write failed for {plate}: {redis_err}")

    # Notify — pass checkpoint type so SMS service knows what happened
    notify_if_needed(db, plate, event_floor, status, cp_type)

    return {
        "plate": plate,
        "checkpoint": event.checkpoint,
        "checkpoint_type": cp_type,
        "status": status,
        "floor": state_floor,
        "timestamp": event.timestamp.isoformat(),
    }


