from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _get_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _build_message(plate: str, floor: int | None, status: str) -> str:
    if status == "exited":
        return f"Your vehicle {plate} has exited the parking facility."
    if floor is not None:
        return f"Your vehicle {plate} is now on Floor {floor}."
    return f"Your vehicle {plate} status updated: {status}."


def send_sms(to_number: str, plate: str, floor: int | None, status: str) -> bool:
    """Send SMS notification. Returns True on success, False on failure."""
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
        logger.warning("Twilio credentials not configured — skipping SMS")
        return False

    try:
        client = _get_client()
        message = _build_message(plate, floor, status)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number,
        )
        logger.info(f"SMS sent to {to_number} for plate {plate}")
        return True
    except TwilioRestException as e:
        logger.error(f"Twilio error for {plate}: {e}")
        return False