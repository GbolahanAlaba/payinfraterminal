from typing import Any

from payments.paystack.base import PaystackBase


class Subaccounts(PaystackBase):
    """
    A class for managing Paystack Subaccounts-related functionality.
    """

    def create_subaccount(
        self,
        business_name: str,
        settlement_bank: str,
        account_number: str,
        percentage_charge: float = 0.0,
        description: str | None = None,
        primary_contact_email: str | None = None,
        primary_contact_name: str | None = None,
        primary_contact_phone: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create a subaccount for an artist or business.

        Args:
            business_name (str): The name of the subaccount owner (artist/business).
            settlement_bank (str): The bank code (e.g., '058' for Access Bank).
            account_number (str): The real bank account number for payouts.
            percentage_charge (float): Optional commission on payments (default 0%).
            description (str, optional): Optional description for the subaccount.
            primary_contact_email (str, optional): Contact email.
            primary_contact_name (str, optional): Contact name.
            primary_contact_phone (str, optional): Contact phone number.
            kwargs: Additional optional parameters.

        Returns:
            Dict[str, Any]: API response from Paystack.
        """
        url = "/subaccount"
        payload = {
            "business_name": business_name,
            "settlement_bank": settlement_bank,
            "account_number": account_number,
            "percentage_charge": percentage_charge,
        }
        if description:
            payload["description"] = description
        if primary_contact_email:
            payload["primary_contact_email"] = primary_contact_email
        if primary_contact_name:
            payload["primary_contact_name"] = primary_contact_name
        if primary_contact_phone:
            payload["primary_contact_phone"] = primary_contact_phone

        payload.update(kwargs)
        return self.post(url, json=payload)

    def list_subaccounts(self, **kwargs) -> dict[str, Any]:
        """
        Retrieve a list of all subaccounts.

        Args:
            kwargs: Optional filters (e.g., perPage, page, active).

        Returns:
            Dict[str, Any]: API response from Paystack.
        """
        url = "/subaccount"
        return self.get(url, params=kwargs)

    def fetch_subaccount(self, subaccount_code: str) -> dict[str, Any]:
        """
        Fetch details of a specific subaccount.

        Args:
            subaccount_code (str): The unique code of the subaccount.

        Returns:
            Dict[str, Any]: API response from Paystack.
        """
        url = f"/subaccount/{subaccount_code}"
        return self.get(url)
