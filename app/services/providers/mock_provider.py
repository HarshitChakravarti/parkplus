import logging
import json
from datetime import datetime
from app.services.checkpoint_service import (
    GATE_ENTRY, FLOOR_ENTRY, FLOOR_EXIT, GATE_EXIT
)
from app.services.notification_provider import NotificationProvider

logger = logging.getLogger(__name__)


def build_message(plate: str, floor: int | None, checkpoint_type: str) -> str:
    if checkpoint_type == GATE_ENTRY:
        return f"Welcome! Your vehicle *{plate}* has entered the parking facility."
    if checkpoint_type == FLOOR_ENTRY and floor is not None:
        return f"Your vehicle *{plate}* has entered *Floor {floor}*."
    if checkpoint_type == FLOOR_EXIT and floor is not None:
        return f"Your vehicle *{plate}* has exited *Floor {floor}*."
    if checkpoint_type == GATE_EXIT:
        return f"Your vehicle *{plate}* has exited the parking facility. Drive safe!"
    return f"Vehicle {plate} checkpoint update recorded."


class MockProvider(NotificationProvider):
    """
    Simulates WhatsApp delivery.
    Logs to console + publishes to WebSocket inbox panel.
    Zero external dependencies.
    """

    def send(self, to_number: str, plate: str, floor: int | None, checkpoint_type: str) -> bool:
        message = build_message(plate, floor, checkpoint_type)
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Pretty console log — looks like real WhatsApp delivery
        logger.info(f"""
╔══════════════════════════════════════╗
║  📱 WHATSAPP  [SIMULATED]            ║
║  To:      {to_number:<27} ║
║  Plate:   {plate:<27} ║
║  Time:    {timestamp:<27} ║
╠══════════════════════════════════════╣
║  {message[:38]:<38} ║
╚══════════════════════════════════════╝""")

        # Publish to WebSocket so dashboard inbox panel updates live
        from app.ws_manager import manager
        import asyncio
        notification_event = {
            "type": "whatsapp_notification",
            "to": to_number,
            "plate": plate,
            "message": message,
            "checkpoint_type": checkpoint_type,
            "timestamp": timestamp,
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(manager.broadcast(notification_event))
            else:
                loop.run_until_complete(manager.broadcast(notification_event))
        except Exception as e:
            logger.warning(f"WebSocket broadcast for notification failed: {e}")

        return True
