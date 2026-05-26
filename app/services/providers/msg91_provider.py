import requests
import logging
from app.config import settings
from app.services.notification_provider import NotificationProvider
from app.services.providers.mock_provider import build_message

logger = logging.getLogger(__name__)


class MSG91Provider(NotificationProvider):
    """
    Production WhatsApp delivery via MSG91.
    Only active when MSG91_AUTH_KEY and MSG91_TEMPLATE_IDs are set in .env
    """

    TEMPLATE_IDS = {
        "gate_entry":  "",   # fill after MSG91 template approval
        "floor_entry": "",
        "floor_exit":  "",
        "gate_exit":   "",
    }

    def send(self, to_number: str, plate: str, floor: int | None, checkpoint_type: str) -> bool:
        if not settings.MSG91_AUTH_KEY:
            logger.error("MSG91_AUTH_KEY not configured")
            return False

        template_id = self.TEMPLATE_IDS.get(checkpoint_type)
        if not template_id:
            logger.error(f"No MSG91 template ID configured for {checkpoint_type}")
            return False

        mobile = to_number.lstrip("+")

        payload = {
            "flow_id": template_id,
            "sender": settings.MSG91_SENDER_ID,
            "mobiles": mobile,
            "VAR1": plate,
            "VAR2": str(floor) if floor else "",
        }

        try:
            res = requests.post(
                "https://api.msg91.com/api/v5/flow/",
                json=payload,
                headers={
                    "authkey": settings.MSG91_AUTH_KEY,
                    "content-type": "application/json"
                },
                timeout=10
            )
            if res.status_code == 200:
                logger.info(f"MSG91 WhatsApp sent to {to_number} for {plate} [{checkpoint_type}]")
                return True
            else:
                logger.error(f"MSG91 error: {res.status_code} {res.text}")
                return False
        except Exception as e:
            logger.error(f"MSG91 request failed: {e}")
            return False
