import logging
import uuid
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db import transaction as db_transaction

from connectors.payments.providers import PAYMENT_PROVIDERS

log = logging.getLogger("my_logger")


class PaymentService:
    """
    Central payment service.

    Responsibilities:
    - Initialize payment with provider (Paystack)
    - Create pending wallet transactions
    - Finalize payment via webhook
    - Split donation (artist + platform commission)
    """

    payment_providers = PAYMENT_PROVIDERS

    def __init__(self, provider_name: str, secret_key: str):
        if not self.payment_providers:
            raise ImproperlyConfigured("No active payment providers configured")

        provider_name = provider_name.lower()

        if provider_name not in self.payment_providers:
            raise ImproperlyConfigured(
                f"Payment provider '{provider_name}' not supported"
            )

        self.provider_name = provider_name
        self.secret_key = secret_key
        self.provider_class = self.payment_providers[provider_name]

    # ---------------------------------------------------------------------
    def get_provider_instance(self):
        """
        Returns provider instance with merchant secret key.
        """
        return self.provider_class(secret_key=self.secret_key)

    # ---------------------------------------------------------------------
    def initialize_payment(
        self,
        *,
        amount: Decimal,
        email: str,
        reference: Optional[str] = None,
        callback_url: Optional[str] = None,
    ):

        if not amount:
            raise ValueError("Amount is required")

        if not email:
            raise ValueError("Email is required")

        amount = Decimal(amount)

        if not reference:
            reference = None

        provider = self.get_provider_instance()

        init_data = provider.initialize_transaction(
            amount=int(amount * 100),
            email=email,
            reference=reference,
            callback_url=callback_url,
            metadata={"amount": str(amount)},
        )

        cleaned_data = provider.clean_init_data(init_data)

        return {
            "status": "success",
            "provider": self.provider_name,
            "provider_data": {"data": init_data,}
            # "payment_url": cleaned_data.get("payment_url"),
            # "reference": cleaned_data.get("reference"),
            # "amount": amount,
        }

            
    # ---------------------------------------------------------------------
    # OPTIONAL: MANUAL VERIFICATION (NOT WEBHOOK)
    # ---------------------------------------------------------------------
    def verify_payment(self, reference: str):
        """
        Optional manual verification endpoint.
        Webhook should always be primary.
        """

        provider_class = self.get_default_provider_class()
        provider = provider_class()

        data = provider.verify_transaction(reference)
        status = data.get("data", {}).get("status")

        if status != "success":
            return {"status": "failed", "message": f"Payment {status}"}

        return {"status": "success", "message": "Payment verified"}
