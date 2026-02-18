import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseProvider:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.name = None


class BasePaymentProvider(abc.ABC):
    """
    Abstract Base Class for Payment Providers.
    Uses an existing API wrapper for making requests.
    """

    def __init__(self, api_client):
        """
        Initialize the provider with an API client.

        :param api_client: Instance of the API wrapper for the provider.
        """
        self.api_client = api_client

    @abc.abstractmethod
    def initialize_transaction(self, email: str, amount: int, **kwargs):
        """
        Initialize a transaction.
        :param kwargs: Additional optional parameters
        :return: A dictionary containing transaction initialization details
        """
        raise NotImplementedError("Initialize transaction is not implemented.")

    @abc.abstractmethod
    def process_payment(
        self,
        amount: float,
        currency: str,
        customer_info: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a payment request.
        :param amount: The payment amount
        :param currency: The currency code (e.g., USD, NGN)
        :param customer_info: Dictionary containing customer details
        :return: A dictionary containing payment response details
        """
        raise NotImplementedError("Process payment is not implemented.")

    @abc.abstractmethod
    def verify_transaction(self, transaction_id: str) -> dict[str, Any]:
        """
        Verify a transaction by ID.
        :param transaction_id: The unique transaction ID
        :return: A dictionary containing transaction verification details
        """
        raise NotImplementedError("Verify transaction is not implemented.")

    @abc.abstractmethod
    def refund_payment(
        self,
        transaction_id: str,
        amount: float | None = None,
    ) -> dict[str, Any]:
        """
        Refund a transaction.
        :param transaction_id: The unique transaction ID
        :param amount: Optional amount to be refunded (default: full refund)
        :return: A dictionary containing refund details
        """
        raise NotImplementedError("Refund payment is not implemented.")

    def handle_response(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handles API responses, logging any errors.

        :param response_data: JSON response from the API
        :return: Processed response
        """
        if "error" in response_data:
            logger.error(response_data["error"])
            return {"success": False, "error": response_data["error"]}

        return {"success": True, "data": response_data}
