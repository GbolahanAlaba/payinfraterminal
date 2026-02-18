from typing import Any

from payments.paystack.base import PaystackBase


class Transactions(PaystackBase):
    """
    A class for handling Paystack transaction-related operations.
    """

    def initialize_transaction(
        self,
        email: str,
        amount: int,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Initialize a transaction.

        Args:
            email (str): Customer's email address.
            amount (int): Amount in kobo (1 Naira = 100 kobo).
            kwargs: Additional optional parameters like 'callback_url', 'metadata', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction/initialize"
        payload = {"email": email, "amount": amount}
        payload.update(kwargs)  # Add optional parameters
        return self.post(url, json=payload)

    def verify_transaction(self, reference: str) -> dict[str, Any]:
        """
        Verify a transaction using its reference.

        Args:
            reference (str): The unique transaction reference.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = f"/transaction/verify/{reference}"
        return self.get(url)

    def list_transactions(self, **kwargs) -> dict[str, Any]:
        """
        Retrieve a list of transactions.

        Args:
            kwargs: Optional filters like 'status', 'customer', 'amount', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction"
        return self.get(url, params=kwargs)

    def fetch_transaction(self, transaction_id: str) -> dict[str, Any]:
        """
        Fetch details of a specific transaction.

        Args:
            transaction_id (int): The unique ID of the transaction.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = f"/transaction/{transaction_id}"
        return self.get(url)

    def charge_authorization(
        self,
        authorization_code: str,
        email: str,
        amount: int,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Charge an existing authorization.

        Args:
            authorization_code (str): Authorization code for the customer.
            email (str): Customer's email address.
            amount (int): Amount in kobo (1 Naira = 100 kobo).
            kwargs: Additional optional parameters like 'metadata', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction/charge_authorization"
        payload = {
            "authorization_code": authorization_code,
            "email": email,
            "amount": amount,
        }
        payload.update(kwargs)  # Add optional parameters
        return self.post(url, json=payload)

    def export_transactions(self, **kwargs) -> dict[str, Any]:
        """
        Export transactions as a CSV file.

        Args:
            kwargs: Optional filters for the export, such as 'status', 'currency', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack, typically with a URL to download the exported file.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction/export"
        return self.get(url, params=kwargs)

    def view_transaction_timeline(self, transaction_id: int) -> dict[str, Any]:
        """
        View the timeline of a transaction.

        Args:
            transaction_id (int): The unique ID of the transaction.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = f"/transaction/timeline/{transaction_id}"
        return self.get(url)

    def transaction_totals(self, **kwargs) -> dict[str, Any]:
        """
        Get totals for transactions.

        Args:
            kwargs: Optional filters like 'from', 'to', 'currency', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction/totals"
        return self.get(url, params=kwargs)

    def partial_debit(
        self,
        authorization_code: str,
        amount: int,
        email: str,
        currency: str = "NGN",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Partially debit a transaction.

        Args:
            transaction_id (int): The unique ID of the transaction.
            amount (int): Amount in kobo (1 Naira = 100 kobo).
            kwargs: Additional optional parameters like 'currency', 'reason', etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        url = "/transaction/partial_debit"
        payload = {
            "authorization_code": authorization_code,
            "currency": currency,
            "amount": amount,
            "email": email,
        }
        payload.update(kwargs)

        return self.post(url, json=payload)
