from abc import ABC, abstractmethod

class BaseWebhookHandler(ABC):

    @abstractmethod
    def verify_signature(self, request) -> bool:
        pass

    @abstractmethod
    def get_event(self, payload: dict) -> str:
        pass

    @abstractmethod
    def extract_payment_data(self, payload: dict) -> dict:
        """
        Must return:
        {
            "reference": str,
            "metadata": dict,
            "status": "success" | "failed"
        }
        """
        pass
