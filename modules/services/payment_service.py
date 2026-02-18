import logging
import uuid
from decimal import Decimal
from typing import Optional
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from modules.payments.providers import PAYMENT_PROVIDERS
from wallet.models import WalletTransaction

log = logging.getLogger('my_logger')


class PaymentService:
    """
    Handles payment actions across dynamically loaded active providers,
    including initialization, verification, and post-payment business logic.
    """

    payment_providers = PAYMENT_PROVIDERS
    log.info(f"Loaded payment providers: {list(payment_providers.keys())}")

    def __init__(self):
        if not self.payment_providers:
            raise ImproperlyConfigured(
                "No active payment providers found. Please activate one in the database."
            )

    def get_default_provider_class(self):
        """
        Returns the first available (active) provider from PAYMENT_PROVIDERS.
        """
        provider_name, provider_class = next(iter(self.payment_providers.items()))
        log.info(f"Using active payment provider: {provider_name}")
        return provider_class

    def initialize_payment(
        self,
        amount: Optional[Decimal] = None,
        user=None,
        transaction_model=None,
        description: str = "Payment",
        fund_wallet: bool = False,
        **kwargs
    ):
        """
        Initialize payment with the active provider and create a transaction record.
        """
        email = kwargs.get("email")
        reference = kwargs.get("reference")

        if user and hasattr(user, "email"):
            email = user.email

        if not email:
            raise ValueError("Email is required for payment initialization.")

        if not amount:
            raise ValueError("Amount is required for payment initialization.")

        # Get active provider
        provider_class = self.get_default_provider_class()
        provider_instance = provider_class()
        log.info(f"Initializing payment of {amount} for {email} using {provider_class.__name__}")

        # Generate reference if missing
        if not reference:
            reference = f"PAY-{uuid.uuid4().hex[:10]}"
        kwargs["reference"] = reference

        # Remove email from kwargs to avoid duplicate passing
        kwargs.pop("email", None)

        try:
            # Initialize transaction via provider
            init_data = provider_instance.initialize_transaction(
                amount=int(Decimal(amount) * 100),  # Ensure numeric
                email=email,
                **kwargs,
            )
            log.info(f"Payment initialized with data: {init_data}")
            cleaned_data = provider_instance.clean_init_data(init_data)

            try:
                from account.models import Profile, User
                profile_id = kwargs.get("profile_id")
                profile = Profile.objects.get(profile_id=profile_id)
                creator_currency_wallet = profile.user.wallet.currency_wallets.get(currency__code="NGN")  # assuming NGN
                platform_currency_wallet = User.objects.get(is_superuser=True).wallet.currency_wallets.get(currency__code="NGN")  # platform wallet

                # Create donation transaction with 10% commission automatically
                from wallet.models import WalletTransaction
                WalletTransaction.transaction_data(
                    transaction_type="credit",
                    creator_currency_wallet=creator_currency_wallet,
                    platform_currency_wallet=platform_currency_wallet,
                    donation_amount=Decimal(amount),
                    description=f"Donation from {email}",
                    reference=reference,
                    status="pending"
                )
            except Exception as e:
                log.error(f"Error creating pending transaction: {e}", exc_info=True)
            

            return {
                "status": "success",
                "payment_url": cleaned_data.get("payment_url"),
                "reference": cleaned_data.get("reference"),
                "amount": Decimal(amount),
            }

        except Exception as e:
            log.error(f"Error initializing payment: {e}", exc_info=True)
            return {"status": "failed", "message": str(e)}

    def verify_payment(
        self,
        reference: str,   
    ):
        """
        Verify payment, update transaction, wallet, statement, and notification.
        """
        provider_class = self.get_default_provider_class()
        provider_instance = provider_class()

        try:
            data = provider_instance.verify_transaction(reference)
            status = data.get("data", {}).get("status")
            channel = data.get("data", {}).get("channel")

            if status != "success":
                log.warning(f"Payment verification failed for {reference}: {status}")
                return {"status": "failed", "message": f"Payment {status}."}

            trans = WalletTransaction.objects.filter(reference=reference).first()
            if not trans:
                log.error(f"No transaction found for reference={reference}")
                return {"status": "failed", "message": "Invalid reference ID."}

            if trans.status == "successful":
                log.warning(f"Payment already verified for reference={reference}")
                return {"status": "failed", "message": "Payment already verified."}

            # Update transaction
            trans.status = "successful"
            trans.updated_at = timezone.now()
            trans.save()
            log.info(f"Transaction {reference} marked as successful.")

            # Update balance
            if trans.transaction_type == "credit":
                platform_commission = trans.amount * Decimal("0.10")
                amount = trans.amount - platform_commission
                trans.currency_wallet.balance += Decimal(amount)
            trans.currency_wallet.save()

            return {"status": "success", "message": "Payment verified successfully"}

        except Exception as e:
            log.error(f"Error verifying payment for {reference}: {e}", exc_info=True)
            return {"status": "failed", "message": str(e)}

    def get_payment_options(self):
        """
        Return a list of currently active providers.
        """
        return list(self.payment_providers.keys())

