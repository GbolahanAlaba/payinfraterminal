from django.conf import settings
from modules.webhooks.base import BaseWebhookHandler

class FlutterwaveWebhookHandler(BaseWebhookHandler):

    def verify_signature(self, request) -> bool:
        return request.headers.get("verif-hash") == settings.FLUTTERWAVE_SECRET_HASH

    def get_event(self, payload: dict) -> str:
        return payload.get("event")

    def extract_payment_data(self, payload: dict) -> dict:
        data = payload.get("data", {})
        return {
            "reference": data.get("tx_ref"),
            "metadata": data.get("meta", {}),
            "status": data.get("status")
        }