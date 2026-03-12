"""
PayPal unified client facade.

Composes ``PayPalTransaction``, ``PayPalRefund``, and ``PayPalWebhook``
into a single ``PayPalClient`` class so call-sites don't need to
juggle multiple instances.

Usage::

    from paypal.client import paypal_client

    order = paypal_client.create_order(order_request)
    result = paypal_client.capture_order(order["id"])
    paypal_client.refund_capture(result["capture_id"])
"""
from __future__ import annotations

from .refund import PayPalRefund
from .transaction import PayPalTransaction
from .webhook import PayPalWebhook


class PayPalClient(PayPalTransaction, PayPalRefund, PayPalWebhook):
    """
    Single entry-point for all PayPal operations.

    Inherits from:
      - ``PayPalTransaction``  – create/capture/authorize orders
      - ``PayPalRefund``       – full and partial refunds
      - ``PayPalWebhook``      – signature verification
      - ``PayPalBase``         – auth, HTTP, retry (via the above)

    Configure via ``settings.PAYPAL``::

        PAYPAL = {
            "CLIENT_ID": env("PAYPAL_CLIENT_ID"),
            "CLIENT_SECRET": env("PAYPAL_CLIENT_SECRET"),
            "ENVIRONMENT": "sandbox",   # "sandbox" | "live"
            "WEBHOOK_ID": env("PAYPAL_WEBHOOK_ID"),
            "TIMEOUT": 30,
            "MAX_RETRIES": 3,
        }
    """


# Module-level singleton — import and use directly
paypal_client = PayPalClient()
