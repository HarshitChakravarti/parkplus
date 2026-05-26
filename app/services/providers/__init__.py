from app.config import settings
from app.services.notification_provider import NotificationProvider


def get_provider() -> NotificationProvider:
    """
    Returns the active notification provider based on config.
    
    NOTIFICATION_PROVIDER=mock    → MockProvider  (default, testing)
    NOTIFICATION_PROVIDER=msg91   → MSG91Provider (production)
    NOTIFICATION_PROVIDER=twilio  → TwilioSandboxProvider (optional)
    """
    provider = settings.NOTIFICATION_PROVIDER.lower()

    if provider == "msg91":
        from app.services.providers.msg91_provider import MSG91Provider
        return MSG91Provider()
        
    if provider == "twilio":
        from app.services.providers.twilio_provider import TwilioSandboxProvider
        return TwilioSandboxProvider()

    # Default — mock for all other values including "mock"
    from app.services.providers.mock_provider import MockProvider
    return MockProvider()
