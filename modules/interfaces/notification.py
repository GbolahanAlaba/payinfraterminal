from abc import ABC, abstractmethod


class BaseNotification(ABC):
    """
    Abstract interface for a NotificationService implementation.
    """

    @abstractmethod
    def send_email(self, data: dict) -> bool:
        pass

    @abstractmethod
    def send_sms(self, to: str, message: str) -> bool:
        pass

    @abstractmethod
    def send_inapp(self, user, title: str, message: str) -> bool:
        pass

    @abstractmethod
    def send_push(self, device_token: str, title: str, body: str) -> bool:
        pass

    @abstractmethod
    def send(self, channels: list, **kwargs) -> dict:
        """
        Main entry point: dispatch notifications to multiple channels.
        Must return a dict of channel results.
        """
        pass
