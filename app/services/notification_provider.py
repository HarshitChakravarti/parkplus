from abc import ABC, abstractmethod

class NotificationProvider(ABC):
    """Base class — all providers must implement this."""

    @abstractmethod
    def send(self, to_number: str, plate: str, floor: int | None, checkpoint_type: str) -> bool:
        pass
