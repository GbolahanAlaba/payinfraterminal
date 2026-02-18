import logging
import uuid
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db import transaction as db_transaction

from modules.payments.providers import PAYMENT_PROVIDERS
from wallet.models import WalletTransaction
from account.models import User, Profile

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

    def __init__(self):
        if not self.payment_providers:
            raise ImproperlyConfigured(
                "No active payment providers configured"
            )

    # ---------------------------------------------------------------------
    # PROVIDER
    # ---------------------------------------------------------------------
    def get_default_provider_class(self):
        """
        Returns the first active payment provider.
        """
        provider_name, provider_class = next(iter(self.payment_providers.items()))
        log.info(f"Using payment provider: {provider_name}")
        return provider_class

    # ---------------------------------------------------------------------
    # PAYMENT INITIALIZATION (NO MONEY MOVES HERE)
    # ---------------------------------------------------------------------
    def initialize_payment(
        self,
        *,
        amount: Optional[Decimal],
        net_amount: Optional[Decimal],
        email: str,
        profile_id: str,
        reference: Optional[str] = None,
        description: str = "Donation",
        
    ):
        """
        Step 1:
        - Initialize payment with Paystack
        - Create a PENDING donation transaction
        - DO NOT credit any wallet yet
        """

        if not amount:
            raise ValueError("Amount is required")

        if not email:
            raise ValueError("Email is required")

        if not profile_id:
            raise ValueError("profile_id is required")
        
        if not amount:
            raise ValueError("Amount is required for payment initialization.")

        amount = Decimal(amount)

        provider_class = self.get_default_provider_class()
        provider = provider_class()
        log.info(f"Initializing payment of {amount} for {email} using {provider_class.__name__}")

        if not reference:
            reference = f"PAY-{uuid.uuid4().hex[:10]}"

        log.info(f"Initializing payment {reference} for {email}")

        # ---- Initialize with Paystack ----
        init_data = provider.initialize_transaction(
            amount=int(amount * 100),  # Paystack expects kobo
            email=email,
            reference=reference,
            metadata={
                "profile_id": profile_id,
                "description": description,
                "net_amount": str(net_amount),
            },
        )
        log.info(f"Payment initialized with data: {init_data}")

        cleaned_data = provider.clean_init_data(init_data)

        # ---- Create pending wallet transaction ----
        profile = Profile.objects.get(profile_id=profile_id)
        creator_currency_wallet = profile.user.wallet.currency_wallets.get(currency__code="NGN")
        platform_currency_wallet = User.objects.get(is_superuser=True).wallet.currency_wallets.get(currency__code="NGN") 
        
        WalletTransaction.transaction_data(
            creator_currency_wallet=creator_currency_wallet,
            platform_currency_wallet=platform_currency_wallet,
            donation_amount=Decimal(net_amount),
            description=f"Donation from {email}",
            reference=reference,
            status="pending"
        )

        return {
            "status": "success",
            "payment_url": cleaned_data.get("payment_url"),
            "reference": reference,
            "amount": amount,
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
