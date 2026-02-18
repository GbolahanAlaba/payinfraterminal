import hmac
import hashlib
import logging
from django.conf import settings

from modules.services.payment_service import PaymentService
from modules.webhooks.base import BaseWebhookHandler
from modules.services.webhook import WebhookLogService

log = logging.getLogger(__name__)


class PaystackWebhookHandler(BaseWebhookHandler):

    def verify_signature(self, request):

        if settings.DEBUG:
            log.warning("DEBUG mode: Paystack webhook signature verification skipped")
            return True
        
        signature = request.headers.get("X-Paystack-Signature")
        if not signature:
            return False

        secret = settings.PAYMENT_PROVIDER["PAYSTACK"]["secret_keys"][
            settings.PAYMENT_PROVIDER["PAYSTACK"]["mode"]
        ]

        computed_hash = hmac.new(
            key=bytes(secret, "utf-8"),
            msg=request.body,
            digestmod=hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(computed_hash, signature)


    def get_event(self, payload: dict) -> str:
        return payload.get("event")

    def extract_payment_data(self, payload: dict) -> dict:
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        customer = data.get("customer", {})

        WebhookLogService(
            payload=data,
            status="success",
            provider="paystack",
        ).create_log()

        return {
            "reference": data.get("reference"),
            "metadata": metadata,
            "customer": customer,
            "status": "success" if payload.get("event") == "charge.success" else "failed"
        }
    
        


    # @csrf_exempt
    # def paystack_webhook(request):
    #     if request.method != "POST":
    #         return HttpResponse(status=405)

    #     if not verify_paystack_signature(request):
    #         return HttpResponse(status=400)

    #     payload = json.loads(request.body)
    #     if payload.get("event") != "charge.success":
    #         return HttpResponse(status=200)

    #     data = payload["data"]
    #     reference = data["reference"]
    #     metadata = data.get("metadata", {})

    #     try:
    #         PaymentService().process_webhook_payment(
    #             reference=reference,
    #             metadata=metadata
    #         )
    #     except Exception as e:
    #         log.error(f"Webhook error: {e}", exc_info=True)
    #         return HttpResponse(status=500)

    #     return HttpResponse(status=200)





