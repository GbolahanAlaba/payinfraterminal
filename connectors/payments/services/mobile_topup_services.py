import logging
import uuid
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from connectors.payments.providers import PAYMENT_PROVIDERS

log = logging.getLogger("my_logger")


class MobileTopupService:
    """
    Central payment service with unified responses.
    """

    payment_providers = PAYMENT_PROVIDERS

    def __init__(self, provider_name: str, credentials: str, environment: str, callback_url=None):
        if not self.payment_providers:
            raise ImproperlyConfigured("No active payment providers configured")

        provider_name = provider_name.lower()
        if provider_name not in self.payment_providers:
            raise ImproperlyConfigured(
                f"Payment provider '{provider_name}' not supported"
            )

        self.provider_name = provider_name
        self.credentials = credentials
        self.environment = environment
        self.callback_url = callback_url
        self.provider_class = self.payment_providers[provider_name]

    def get_provider_instance(self):
        """Return provider instance with merchant credentials."""
        return self.provider_class(credentials=self.credentials, environment=self.environment, callback_url=self.callback_url)


    def initialize_mobile_recharge(
        self,
        *,
        topup_type: str,
        network: str,
        phone_number: str,
        amount: Decimal,
        sender_name: str,
        reference: Optional[str] = None,
    ):
        """Initialize payment and return unified response."""
        if not network or not phone_number or not amount:
            raise ValueError("network and phone number and amount are required")

        provider = self.get_provider_instance()

        if topup_type == "airtime":
            init_data = provider.buy_airtime(
                network=network,
                phone_number=phone_number,
                amount=int(amount),
                reference=reference or str(uuid.uuid4()),
                sender_name=sender_name
            )
        else:
            init_data = provider.buy_data(
                network=network,
                phone_number=phone_number,
                amount=int(amount),
                reference=reference or str(uuid.uuid4()),
                sender_name=sender_name
            )
        
        print(init_data)
        cleaned_data = provider.topup_clean_init_data(init_data)
        return cleaned_data

    def verify_payment(self, reference: str):
        provider = self.get_provider_instance()
        raw_data = provider.verify_transaction(reference)

        # cleaned_data = provider.clean_init_data(raw_data)
        print(raw_data)
        return raw_data

    
    # def verify_payment(self, reference: str, amount: Decimal):
    #     """Manual verification with unified response."""
    #     provider = self.get_provider_instance()
    #     raw_data = provider.verify_transaction(reference)

    #     # Use provider's clean_init_data if available
    #     cleaned_data = provider.clean_init_data(raw_data)

    #     return self._unify_response(cleaned_data, raw_data, amount)

