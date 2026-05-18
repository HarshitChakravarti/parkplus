from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.models.vehicle_state import CurrentVehicleState
from app.services.sms_service import send_sms
import logging

logger = logging.getLogger(__name__)


def should_notify(previous_state: CurrentVehicleState | None, new_floor: int | None, new_status: str) -> bool:
    """Decide whether this state change warrants an SMS."""
    if previous_state is None:
        return True  # First time we've seen this vehicle

    if new_status == "exited" and previous_state.status != "exited":
        return True  # Vehicle just left

    if previous_state.current_floor != new_floor and new_status == "inside":
        return True  # Floor changed

    return False  # Same floor, no meaningful change


def notify_if_needed(
    db: Session,
    plate: str,
    new_floor: int | None,
    new_status: str,
    previous_state: CurrentVehicleState | None,
):
    if not should_notify(previous_state, new_floor, new_status):
        return

    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle or not vehicle.owner_phone:
        logger.info(f"No phone number for {plate} — skipping SMS")
        return

    send_sms(vehicle.owner_phone, plate, new_floor, new_status)