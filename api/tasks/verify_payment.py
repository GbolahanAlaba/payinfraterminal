# tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction as db_transaction

from transactions.models import Transaction, STATUS
from connectors.payments.services.payment_services import PaymentService
from routing.engine import PaymentRouteEngine

log = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def verify_processing_transactions(self):

    processing_transactions = Transaction.objects.filter(
        status=STATUS.PROCESSING
    ).only("id", "reference", "preferred_provider")

    for tx in processing_transactions:

        if not tx.reference:
            continue

        try:
            api_client = tx.merchant.api_clients.first()
            engine = PaymentRouteEngine(client=api_client)
            credentials = engine.get_provider_credentials(tx.preferred_provider)
            service = PaymentService(
                provider_name=tx.preferred_provider,
                secret_key=credentials["secret_key"]
            )
            response = service.verify_payment(tx.reference)
            log.info({f"VERIFICATION RESPONSE: {response}"})

            status = response.get("status")
            message = response.get("message", "")

            with db_transaction.atomic():

                if status == "success":

                    tx.status = STATUS.SUCCESS
                    tx.completed_at = timezone.now()

                elif status == "failed":

                    tx.status = STATUS.FAILED
                    tx.completed_at = timezone.now()

                else:
                    # still pending or processing
                    continue

                tx.message = message
                tx.save(update_fields=[
                    "status",
                    "message",
                    "completed_at",
                    "updated_at"
                ])

        except Exception as e:
            # optionally log error
            print(f"Verification failed for {tx.reference}: {str(e)}")