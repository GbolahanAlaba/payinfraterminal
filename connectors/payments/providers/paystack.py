import logging
from typing import Any
from django.conf import settings
from connectors.payments.providers.base import BasePaymentProvider
from connectors.payments.paystack.paystack import PaystackClient

log = logging.getLogger("my_logger")


class PaystackProvider(BasePaymentProvider):
    """
    Paystack Payment Provider Implementation.
    Supports dynamic secret keys per merchant.
    """

    def __init__(self, secret_key: str, callback_url: str = None):
        """
        :param secret_key: Merchant Paystack secret key
        :param callback_url: Optional override callback URL
        """

        if not secret_key:
            raise ValueError("Paystack secret key is required.")

        self.secret_key = secret_key
        self.callback_url = callback_url or getattr(
            settings, "PAYSTACK_CALLBACK_URL", None
        )

        super().__init__(api_client=PaystackClient(secret_key=secret_key))
        self.name = "paystack"

    # ------------------------------------------------------------------
    # INITIALIZE
    # ------------------------------------------------------------------
    def initialize_transaction(self, *, email, amount, reference, metadata=None):

        amount = int(amount)  # already converted to kobo before this ideally

        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
            "metadata": metadata or {},
        }

        if self.callback_url:
            payload["callback_url"] = self.callback_url

        return self.api_client.transactions.initialize_transaction(**payload)

    def verify_transaction(self, transaction_id):
        return self.api_client.transactions.verify_transaction(transaction_id)

    def clean_init_data(self, init_data):
        data = init_data.get("data", {})

        return {
            "payment_url": data.get("authorization_url"),
            "access_code": data.get("access_code"),
            "reference": data.get("reference"),
            "metadata": data.get("metadata"),

            # "raw": init_data,
        }

    def process_payment(self, transaction_id):
        return self.api_client.transactions.process_payment(transaction_id)

    def refund_payment(self, transaction_id):
        return self.api_client.transactions.refund_payment(transaction_id)

   
    def list_banks(self, params=None):
        """
        List banks and return only name and code for each bank.
        """
        raw_data = self.api_client.miscellaneous.list_banks(params=params)

        # If raw_data is a dict with 'data', extract it; else assume it's a list
        if isinstance(raw_data, dict):
            banks = raw_data.get("data", [])
        elif isinstance(raw_data, list):
            banks = raw_data
        else:
            banks = []

        # Transform to only include name and code
        cleaned_banks = [{"name": bank.get("name"), "code": bank.get("code")} for bank in banks]

        return cleaned_banks
    
    def resolve_account(self, account_number: str, bank_code: str) -> dict:
        import requests
        try:
            result = self.api_client.verification.resolve_account_number(account_number, bank_code)
            paystack_data = result.get("data", {})
            return {
                "accountName": paystack_data.get("account_name"),
                "accountNumber": paystack_data.get("account_number")
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                raise Exception("Paystack API rate limit exceeded. Try again later.")
            raise

    # =========================
    # Transfers
    # =========================

    def create_transfer_recipient(
        self,
        name: str,
        account_number: str,
        bank_code: str,
        currency: str = "NGN",
        **kwargs,
    ):
        return self.api_client.transfer.create_transfer_recipient(
            name=name,
            account_number=account_number,
            bank_code=bank_code,
            currency=currency,
            **kwargs,
        )

    def initiate_transfer(
        self,
        amount: int,
        recipient: str,
        reason: str | None = None,
        source: str = "balance",
        **kwargs,
    ):
        """
        Initiate a single transfer.

        amount: Amount in kobo
        recipient: Recipient code from Paystack
        """
        return self.api_client.transfer.initiate_transfer(
            source=source,
            amount=int(amount),
            recipient=recipient,
            reason=reason,
            **kwargs,
        )

    def finalize_transfer(self, transfer_code: str, otp: str):
        """
        Finalize a transfer using OTP.
        """
        return self.api_client.transfer.finalize_transfer(
            transfer_code=transfer_code,
            otp=otp,
        )

    def initiate_bulk_transfer(self, transfers: list[dict]):
        """
        Initiate bulk transfers.

        transfers example:
        [
            {"amount": 50000, "recipient": "RCP_xxx", "reference": "ref1"},
            {"amount": 30000, "recipient": "RCP_yyy", "reference": "ref2"},
        ]
        """
        return self.api_client.transfer.initiate_bulk_transfer(transfers)

    def list_transfers(self, **filters):
        """
        List transfers with optional filters.
        """
        return self.api_client.transfer.list_transfers(**filters)

    def fetch_transfer(self, transfer_id: str):
        """
        Fetch a single transfer by ID.
        """
        return self.api_client.transfer.fetch_transfer(transfer_id)

    def verify_transfer(self, reference: str):
        """
        Verify a transfer using reference.
        """
        return self.api_client.transfer.verify_transfer(reference)


    # =========================
    # Subaccounts
    # =========================

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
            business_name (str): The name of the artist/business.
            settlement_bank (str): Bank code (e.g., '058' for Access Bank).
            account_number (str): Real bank account number.
            percentage_charge (float): Optional commission on payments.
            description (str, optional): Subaccount description.
            primary_contact_email (str, optional): Contact email.
            primary_contact_name (str, optional): Contact name.
            primary_contact_phone (str, optional): Contact phone.
            kwargs: Additional optional parameters.

        Returns:
            dict[str, Any]: API response from Paystack.
        """
        return self.api_client.subaccounts.create_subaccount(
            business_name=business_name,
            settlement_bank=settlement_bank,
            account_number=account_number,
            percentage_charge=percentage_charge,
            description=description,
            primary_contact_email=primary_contact_email,
            primary_contact_name=primary_contact_name,
            primary_contact_phone=primary_contact_phone,
            **kwargs,
        )

    def list_subaccounts(self, **kwargs) -> dict[str, Any]:
        """
        Retrieve all subaccounts.

        Args:
            kwargs: Optional filters (perPage, page, active).

        Returns:
            dict[str, Any]: API response from Paystack.
        """
        return self.api_client.subaccounts.list_subaccounts(**kwargs)

    def fetch_subaccount(self, subaccount_code: str) -> dict[str, Any]:
        """
        Fetch details of a specific subaccount by code.

        Args:
            subaccount_code (str): Unique subaccount code.

        Returns:
            dict[str, Any]: API response from Paystack.
        """
        return self.api_client.subaccounts.fetch_subaccount(subaccount_code)



    # def list_banks(self, params=None):
    #     return self.api_client.miscellaneous.list_banks(params=params)
    
    # def resolve_account(self, account_number: str, bank_code: str) -> dict[str, Any]:
    #     return self.api_client.verification.resolve_account_number(
    #         account_number, bank_code
    #     )
