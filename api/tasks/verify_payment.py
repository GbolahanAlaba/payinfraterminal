# tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction as db_transaction

from transactions.models import Transaction, STATUS, TRANSACTION_TYPE
from connectors.payments.services.payment_services import PaymentService
from routing.engine import PaymentRouteEngine

log = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def verify_processing_transactions(self):

    processing_transactions = (
        Transaction.objects
        .filter(status=STATUS.PROCESSING, transaction_type=TRANSACTION_TYPE.COLLECTION)
        .select_related("merchant", "api_client")
        .only(
            "id",
            "reference",
            "preferred_provider",
            "api_client",
            "merchant"
        )
    )

    for tx in processing_transactions:

        if not tx.reference:
            continue

        try:

            engine = PaymentRouteEngine(client=tx.api_client)

            credentials = engine.get_provider_credentials(
                tx.preferred_provider)
            
            # log.info(f"credentials {credentials}")

            service = PaymentService(
                provider_name=tx.preferred_provider,
                secret_key=credentials["secret_key"]
            )

            response = service.verify_payment(tx.reference, tx.amount)

            # log.info(f"Verification response for {tx.reference}: {response}")

            if tx.preferred_provider == "paystack":
                top_data = response.get("data", {})        # wrapper
                inner_data = top_data.get("data", {})      # actual transaction payload

                authorization = inner_data.get("authorization")  # may exist or None

                # Get channel safely
                channel = authorization.get("channel") if authorization else inner_data.get("channel")

                log.info(f"Authorization: {authorization}")
                log.info(f"Channel: {channel}")
                if provider_status in [True, "success", "Successful"]:
                    provider_status = "success"

                elif provider_status in [False, "failed"]:
                    provider_status = "failed"

                else:
                    provider_status = "processing"
                message = response.get("message", "")

            with db_transaction.atomic():

                if provider_status == "success":
                    tx.status = STATUS.SUCCESS
                    tx.channel = channel
                    tx.metadata = top_data
                    tx.completed_at = timezone.now()

                elif provider_status in ["failed", "abandoned"]:
                    tx.status = STATUS.FAILED
                    tx.completed_at = timezone.now()

                else:
                    continue

                tx.message = message

                tx.save(update_fields=[
                    "status",
                    "channel",
                    "metadata",
                    "message",
                    "completed_at",
                    "updated_at"
                ])
                log.info(f"VERIFICATION COMPLETED FOR {tx.merchant} | REF {tx.reference}")

        except Exception as e:

            log.error(
                f"Verification failed for {tx.reference}: {str(e)}"
            )