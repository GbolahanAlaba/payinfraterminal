import logging
from decimal import Decimal
from django.conf import settings
from django.db import transaction as db_transaction
from wallet.models import WalletTransaction
from account.models import User, Profile
from transaction.models import WebhookLog
from modules.services.notification_service import NotificationService
from modules.utils.emails import support_gift_email

service = NotificationService()

log = logging.getLogger("my_logger")


class WebhookService:

     def process_webhook_payment(self, reference: str, metadata: dict):
        """
        Step 2:
        - Called ONLY by webhook
        - Marks transaction successful
        - Splits donation
        - Credits artist wallet
        - Credits platform commission wallet
        """

        net_amount = Decimal(metadata.get("net_amount"))

        with db_transaction.atomic():

            trans = (
                WalletTransaction.objects
                .select_for_update()
                .filter(reference=reference)
                .first()
            )

            if not trans:
                raise ValueError("Transaction not found")

            if trans.status == "successful":
                log.info(f"Duplicate webhook ignored for {reference}")
                return

            # ---- Mark donation successful ----
            trans.status = "successful"
            trans.save()

            profile = Profile.objects.get(profile_id=metadata.get("profile_id"))
            print(f"Profile ID {profile}")

            creator_wallet = profile.user.wallet.currency_wallets.get(currency__code="NGN")

            # ---- Platform wallet ----
            comm_email = settings.COMMISSION_EMAIL
            platform_user = User.objects.get(email=comm_email)
            platform_wallet = platform_user.wallet.currency_wallets.get(currency=creator_wallet.currency)

            # ---- Split donation ----
            platform_commission = net_amount * Decimal("0.10")
            creator_amount = net_amount - platform_commission

            # ---- Credit artist ----
            creator_wallet.balance += creator_amount
            creator_wallet.save()

            # ---- Credit platform ----
            platform_wallet.balance += platform_commission
            platform_wallet.save()

            # ---- Record commission transaction ----
            WalletTransaction.objects.create(
                currency_wallet=creator_wallet,
                transaction_type="debit",
                source="commission",
                amount=platform_commission,
                reference=f"PCOM-{reference}",
                description="Platform commission",
                status="successful",
            )

            WalletTransaction.objects.create(
                currency_wallet=platform_wallet,
                transaction_type="credit",
                source="commission",
                amount=platform_commission,
                reference=f"COM-{reference}",
                description="Platform commission",
                status="successful",
            )

            support_gift_email(profile.user, net_amount)
            service.send(
                channels=["inapp"],
                user=profile.user,
                title = "Support Received!",
                inapp_message = f"Congratulations! ₦{net_amount} has been gifted to you. Keep inspiring lives!"
                )

            log.info(
                f"Payment {reference} processed | "
                f"Creator: {creator_amount}, Platform: {platform_commission}"
            )
            
            
class WebhookLogService:
    def __init__(self, payload: dict, status: str = None, error: str = None, provider: str = None,):
        """
        Initialize the WebhookLogService with payload, status, and error.

        :param payload: The payload data from the webhook.
        :param status: The status of the webhook log (optional).
        :param error: The error message if any (optional).
        """
        self.status = status
        self.error = error
        self.payload = payload
        self.provider = provider

    def create_log(self):
        """
        Create a new webhook log entry.
        """
        WebhookLog.objects.create(
            payload=self.payload,
            status=self.status,
            error=self.error,
            provider=self.provider,
        )

    def update_log(self, status: str, error: str = None):
        log = WebhookLog.objects.get(payload=self.payload)
        log.status = status
        log.error = error
        log.save()

    def get_log(self):
        return WebhookLog.objects.get(payload=self.payload)