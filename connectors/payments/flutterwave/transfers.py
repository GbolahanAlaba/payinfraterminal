# transfers.py
from typing import Dict
from .base import FlutterwaveAPIClient


class FlutterwaveTransfers(FlutterwaveAPIClient):
    """Handle Flutterwave bank transfers."""

    def initiate_transfer(
        self,
        account_bank: str,
        account_number: str,
        amount: float,
        currency: str,
        narration: str,
        reference: str,
        callback_url: str = None,
        debit_currency: str = None,
    ) -> Dict:
        """
        Initiate a Flutterwave bank transfer.
        """
        payload = {
            "account_bank": account_bank,
            "account_number": account_number,
            "amount": amount,
            "narration": narration,
            "currency": currency,
            "reference": reference,
            "debit_currency": debit_currency or currency,
        }

        if callback_url:
            payload["callback_url"] = callback_url

        return self.post("/v3/transfers", data=payload)
