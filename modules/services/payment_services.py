import logging
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from connectors.payments.providers import PAYMENT_PROVIDERS

log = logging.getLogger("my_logger")


class PaymentService:
    """
    Central payment service with unified responses.
    """

    payment_providers = PAYMENT_PROVIDERS

    def __init__(self, provider_name: str, secret_key: str, callback_url=None):
        if not self.payment_providers:
            raise ImproperlyConfigured("No active payment providers configured")

        provider_name = provider_name.lower()
        if provider_name not in self.payment_providers:
            raise ImproperlyConfigured(
                f"Payment provider '{provider_name}' not supported"
            )

        self.provider_name = provider_name
        self.secret_key = secret_key
        self.callback_url = callback_url
        self.provider_class = self.payment_providers[provider_name]

    def get_provider_instance(self):
        """Return provider instance with merchant secret key."""
        return self.provider_class(secret_key=self.secret_key, callback_url=self.callback_url)

    def _unify_response(self, cleaned_data: dict, raw_data: dict) -> dict:
        provider_data = raw_data.get("data", {}).copy()
        provider_data.update(cleaned_data)

        unified_data = {
            "payment_url": provider_data.get("payment_url")
            or provider_data.get("authorization_url")
            or provider_data.get("link"),

            "access_code": provider_data.get("access_code")
            or provider_data.get("tx_ref"),

            "reference": provider_data.get("reference")
            or provider_data.get("tx_ref"),

            "amount": provider_data.get("amount"),
            "currency": provider_data.get("currency") or "NGN",
            "metadata": provider_data.get("metadata") or {},
            "provider": provider_data.get("provider") or self.provider_name,
        }

        # fields that are aliases of unified fields
        alias_fields = {
            "authorization_url",
            "link",
            "tx_ref",
            "payment_url",
            "reference",
            "access_code",
        }

        extra_fields = {
            k: v for k, v in provider_data.items()
            if k not in unified_data and k not in alias_fields
        }

        unified_data.update(extra_fields)

        return {
            "status": cleaned_data.get("status") or raw_data.get("status") or "success",
            "message": cleaned_data.get("message") or raw_data.get("message") or "Transaction initialized",
            "data": unified_data,
        }


    def initialize_payment(
        self,
        *,
        amount: Decimal,
        email: str,
        reference: Optional[str] = None,
        callback_url: Optional[str] = None,
    ):
        """Initialize payment and return unified response."""
        if not amount or not email:
            raise ValueError("Amount and email are required")

        provider = self.get_provider_instance()

        init_data = provider.initialize_transaction(
            amount=int(amount * 100),
            email=email,
            reference=reference,
            callback_url=callback_url,
            metadata={"amount": str(amount)},
        )

        # Use provider's clean_init_data
        cleaned_data = provider.clean_init_data(init_data)

        # Return unified response with fallback
        cleaned_data = provider.clean_init_data(init_data)
        response = self._unify_response(cleaned_data, init_data)
        return response

    def verify_payment(self, reference: str):
        """Manual verification with unified response."""
        provider = self.get_provider_instance()
        raw_data = provider.verify_transaction(reference)

        # Use provider's clean_init_data if available
        cleaned_data = provider.clean_init_data(raw_data)

        return self._unify_response(cleaned_data, raw_data)

