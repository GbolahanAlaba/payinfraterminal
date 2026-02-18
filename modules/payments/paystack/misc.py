from typing import Any

from modules.payments.paystack.base import PaystackBase


class Miscellaneous(PaystackBase):
    """
    A class for managing Paystack Miscellaneous-related functionality.
    """

    def list_banks(self, params=None, **kwargs) -> dict[str, Any]:
        """
        List all banks supported by Paystack.

        Args:
            kwargs: Optional filters like `currency` (e.g., "NGN"), `type` (e.g., "nuban"), or `country` (e.g., "NG").

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = "/bank"
        return self.get(url, params=params)

    def list_search_countries(self) -> dict[str, Any]:
        """
        List all countries supported by Paystack.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"{self.base_url}/country"
        return self.get(url)

    def list_states(self, country_code: str | None = None) -> dict[str, Any]:
        """
        List states for a specific country (for AVS).

        Args:
            country_code (Optional[str]): The country code (e.g., "NG" for Nigeria). If not provided, defaults to Nigeria.

        Returns:
            Dict[str, Any]: The API response from Paystack.
        """
        url = f"{self.base_url}/address_verification/states"
        params = {"country": country_code} if country_code else {}
        return self.get(url, params=params)
