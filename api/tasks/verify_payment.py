# tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction as db_transaction

from transactions.models import Transaction, STATUS, TRANSACTION_TYPE
from api.views import VerifyTransactionView
from connectors.payments.services.payment_services import PaymentService
from routing.engine import PaymentRouteEngine

log = logging.getLogger(__name__)



def verify_paystack():

    pass

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
            
            if tx.preferred_provider == "paystack":
                paystack_data = VerifyTransactionView.__paystack__(self, tx.reference, credentials)

                metadata = paystack_data["metadata"]
                provider_status = paystack_data["provider_status"]
                channel = paystack_data["channel"]
                message = paystack_data["message"]
                response = paystack_data["response"]

            if tx.preferred_provider == "flutterwave":
                flutterwave_data = VerifyTransactionView.__flutterwave__(self, tx.reference, credentials)

                metadata = flutterwave_data["metadata"]
                provider_status = flutterwave_data["provider_status"]
                channel = flutterwave_data["channel"]
                message = flutterwave_data["message"]
                response = flutterwave_data["response"]

            with db_transaction.atomic():

                if provider_status == "success":
                    tx.metadata = metadata
                    tx.status = STATUS.SUCCESS
                    tx.channel = channel
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

