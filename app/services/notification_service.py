from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.services.sms_service import send_sms
from app.services.checkpoint_service import GATE_ENTRY, FLOOR_ENTRY, FLOOR_EXIT, GATE_EXIT, UNKNOWN
import logging

logger = logging.getLogger(__name__)

# These checkpoint types always trigger an SMS if vehicle is registered
NOTIFIABLE_TYPES = {GATE_ENTRY, FLOOR_ENTRY, FLOOR_EXIT, GATE_EXIT}


def notify_if_needed(
    db: Session,
    plate: str,
    floor: int | None,
    status: str,
    checkpoint_type: str,
):
    # Unknown checkpoint format — nothing to notify
    if checkpoint_type == UNKNOWN:
        logger.warning(f"Unknown checkpoint type for {plate} — skipping notification")
        return

    # Only notify on meaningful checkpoint types
    if checkpoint_type not in NOTIFIABLE_TYPES:
        return

    # Look up vehicle registration
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()

    if not vehicle:
        logger.info(f"{plate} not in database — skipping SMS")
        return

    if not vehicle.is_registered:
        logger.info(f"{plate} is unregistered — tracking only, no SMS")
        return

    if not vehicle.owner_phone:
        logger.info(f"{plate} is registered but has no phone number — skipping SMS")
        return

    send_sms(vehicle.owner_phone, plate, floor, checkpoint_type)