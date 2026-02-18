from typing import Any

from payments.paystack.base import PaystackBase


class Transfers(PaystackBase):
    """
    A class for managing Paystack Transfers-related functionality.
    """

    def create_transfer_recipient(
        self,
        name: str,
        account_number: str,
        bank_code: str,
        currency: str = "NGN",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create a transfer recipient.
        """
        url = f"/transferrecipient"
        payload = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": currency,
        }
        payload.update(kwargs)
        return self.post(url, json=payload)

    def initiate_transfer(
        self,
        source: str,
        amount: int,
        recipient: str,
        reason: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Initiate a single transfer.

        Args:
            source (str): The source of the transfer (e.g., "balance").
            amount (int): The amount to transfer (in kobo for NGN).
            recipient (str): The recipient code.
            reason (Optional[str]): The reason for the transfer (optional).
            kwargs: Additional optional parameters.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"/transfer"
        payload = {
            "source": source,
            "amount": amount,
            "recipient": recipient,
        }
        if reason:
            payload["reason"] = reason
        payload.update(kwargs)
        return self.post(url, json=payload)

    def finalize_transfer(self, transfer_code: str, otp: str) -> dict[str, Any]:
        """
        Finalize a transfer with an OTP.

        Args:
            transfer_code (str): The code of the transfer to finalize.
            otp (str): The OTP to finalize the transfer.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"/transfer/finalize_transfer"
        payload = {
            "transfer_code": transfer_code,
            "otp": otp,
        }
        return self.post(url, json=payload)

    def initiate_bulk_transfer(self, transfers: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Initiate a bulk transfer.

        Args:
            transfers (List[Dict[str, Any]]): A list of transfer objects with recipient and amount details.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"/transfer/bulk"
        payload = {"batch": transfers}
        return self.post(url, json=payload)

    def list_transfers(self, **kwargs) -> dict[str, Any]:
        """
        Retrieve a list of transfers.

        Args:
            kwargs: Optional filters such as `status`, `perPage`, `page`, etc.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"/transfer"
        return self.get(url, params=kwargs)

    def fetch_transfer(self, transfer_id: str) -> dict[str, Any]:
        """
        Fetch details of a specific transfer.

        Args:
            transfer_id (str): The unique ID of the transfer.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"/transfer/{transfer_id}"
        return self.get(url)

    def verify_transfer(self, transfer_reference: str) -> dict[str, Any]:
        """
        Verify the status of a transfer.

        Args:
            transfer_reference (str): The unique reference of the transfer.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"{self.base_url}/transfer/verify/{transfer_reference}"
        return self.get(url)
