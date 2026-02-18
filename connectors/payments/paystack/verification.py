from typing import Any

from payments.paystack.base import PaystackBase


class Verification(PaystackBase):
    """
    A class for managing Paystack Verification-related functionality.
    """

    def resolve_account_number(
        self,
        account_number: str,
        bank_code: str,
    ) -> dict[str, Any]:
        """
        Resolve an account number to retrieve the account name and other details.

        Args:
            account_number (str): The account number to resolve.
            bank_code (str): The code of the bank associated with the account.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = "/bank/resolve"
        params = {
            "account_number": account_number,
            "bank_code": bank_code,
        }
        return self.get(url, params=params)

    def validate_account(
        self,
        account_name: str,
        account_number: str,
        bank_code: str,
        country_code: str,
    ) -> dict[str, Any]:
        """
        Validate an account by matching the account name with account details.

        Args:
            account_name (str): The name associated with the account.
            account_number (str): The account number to validate.
            bank_code (str): The bank code for the account.
            country_code (str): The country code (e.g., "NG" for Nigeria).

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"{self.base_url}/bank/validate"
        payload = {
            "account_name": account_name,
            "account_number": account_number,
            "bank_code": bank_code,
            "country_code": country_code,
        }
        return self.post(url, json=payload)

    def resolve_card_bin(self, bin_number: str) -> dict[str, Any]:
        """
        Resolve the details of a card using its BIN (Bank Identification Number).

        Args:
            bin_number (str): The first 6 digits of the card number (BIN).

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"{self.base_url}/decision/bin/{bin_number}"
        return self.get(url)
