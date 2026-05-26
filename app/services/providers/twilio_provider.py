from twilio.rest import Client
from app.services.notification_provider import NotificationProvider
from app.services.providers.mock_provider import build_message
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TwilioSandboxProvider(NotificationProvider):

    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    def send(self, to_number, plate, floor, checkpoint_type):

        message = build_message(
            plate,
            floor,
            checkpoint_type
        )

        try:
            self.client.messages.create(
                from_='whatsapp:+14155238886',
                body=message,
                to=f'whatsapp:{to_number}'
            )

            logger.info(
                f"WhatsApp sent to {to_number}"
            )

            return True

        except Exception as e:
            logger.error(
                f"Twilio send failed: {e}"
            )
            return False
