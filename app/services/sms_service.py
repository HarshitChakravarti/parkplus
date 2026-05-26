from app.services.providers import get_provider
import logging

logger = logging.getLogger(__name__)


def send_sms(to_number: str, plate: str, floor: int | None, checkpoint_type: str) -> bool:
    """
    Provider-agnostic notification sender.
    Business logic never knows which provider is active.
    """
    provider = get_provider()
    return provider.send(to_number, plate, floor, checkpoint_type)