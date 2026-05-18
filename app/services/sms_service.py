from app.services.checkpoint_service import (
    GATE_ENTRY, FLOOR_ENTRY, FLOOR_EXIT, GATE_EXIT
)
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _get_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _build_message(plate: str, floor: int | None, checkpoint_type: str) -> str:
    if checkpoint_type == GATE_ENTRY:
        return f"Welcome! Your vehicle {plate} has entered the parking facility."
    if checkpoint_type == FLOOR_ENTRY and floor is not None:
        return f"Your vehicle {plate} has entered Floor {floor}."
    if checkpoint_type == FLOOR_EXIT and floor is not None:
        return f"Your vehicle {plate} has exited Floor {floor}."
    if checkpoint_type == GATE_EXIT:
        return f"Your vehicle {plate} has exited the parking facility. Drive safe!"
    return f"Vehicle {plate} checkpoint update recorded."


def send_sms(to_number: str, plate: str, floor: int | None, checkpoint_type: str) -> bool:
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
        logger.warning(f"Twilio credentials not configured — skipping SMS for {plate} [{checkpoint_type}]")
        return False

    try:
        client = _get_client()
        message = _build_message(plate, floor, checkpoint_type)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number,
        )
        logger.info(f"SMS sent to {to_number} for {plate} [{checkpoint_type}]")
        return True
    except TwilioRestException as e:
        logger.error(f"Twilio error for {plate}: {e}")
        return False