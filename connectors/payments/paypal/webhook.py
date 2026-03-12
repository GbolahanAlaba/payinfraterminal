"""
PayPal webhook module.

Two responsibilities:
  1. ``PayPalWebhook``       – verifies incoming webhook signatures via PayPal API
  2. Event dispatcher/registry – routes verified events to your handler functions
"""
from __future__ import annotations

import logging
from typing import Callable

from .base import PayPalBase
from .exceptions import PayPalError, PayPalWebhookError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Webhook client
# ---------------------------------------------------------------------------

class PayPalWebhook(PayPalBase):
    """Webhook signature verification and event-type introspection."""

    def verify_signature(
        self,
        *,
        transmission_id: str,
        timestamp: str,
        cert_url: str,
        auth_algo: str,
        actual_sig: str,
        body: bytes,
    ) -> bool:
        """
        Verify a PayPal webhook via the official API endpoint.

        Prefer this over manual HMAC — PayPal rotates certs and the API
        handles all edge cases correctly.

        Returns ``True`` when ``verification_status == "SUCCESS"``.
        """
        if not self._webhook_id:
            raise PayPalWebhookError("PAYPAL['WEBHOOK_ID'] is not configured")

        payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": actual_sig,
            "transmission_time": timestamp,
            "webhook_id": self._webhook_id,
            "webhook_event": body.decode("utf-8"),
        }
        try:
            result = self._request(
                "POST",
                "/v1/notifications/verify-webhook-signature",
                json=payload,
            )
            return result.get("verification_status") == "SUCCESS"
        except PayPalError as exc:
            logger.error("Webhook verification API call failed: %s", exc)
            return False

    def list_event_types(self) -> list[dict]:
        """Return all PayPal webhook event types (useful for dashboard setup)."""
        result = self._request("GET", "/v1/notifications/webhooks-event-types")
        return result.get("event_types", [])


# ---------------------------------------------------------------------------
# Event dispatcher registry
# ---------------------------------------------------------------------------

_HANDLERS: dict[str, list[Callable]] = {}


def register(event_type: str) -> Callable:
    """
    Decorator – register a handler for a PayPal webhook event type.

    Multiple handlers per event type are supported and called in order.

    Usage::

        from paypal.webhook import register

        @register("PAYMENT.CAPTURE.COMPLETED")
        def fulfill_order(resource: dict, raw_event: dict) -> None:
            order = Order.objects.get(paypal_capture_id=resource["id"])
            order.mark_paid()
    """
    def decorator(fn: Callable) -> Callable:
        _HANDLERS.setdefault(event_type, []).append(fn)
        return fn
    return decorator


def dispatch(*, event_type: str, resource: dict, raw_event: dict) -> None:
    """
    Dispatch a verified webhook event to all registered handlers.

    Unknown event types are silently ignored (logged at DEBUG).
    Handler exceptions bubble up — the caller (view) is responsible
    for catching them so PayPal never receives a 5xx.
    """
    handlers = _HANDLERS.get(event_type, [])
    if not handlers:
        logger.debug("No handler registered for PayPal event: %s", event_type)
        return
    for handler in handlers:
        handler(resource=resource, raw_event=raw_event)


# ---------------------------------------------------------------------------
# Built-in handler stubs – fill in your business logic
# ---------------------------------------------------------------------------

@register("PAYMENT.CAPTURE.COMPLETED")
def _on_capture_completed(resource: dict, raw_event: dict) -> None:
    """
    Buyer's payment has been successfully captured.

    Key fields:
      resource["id"]                – capture ID
      resource["custom_id"]         – your internal order ID (if set at order creation)
      resource["invoice_id"]        – your invoice reference
      resource["amount"]["value"]   – captured amount
      resource["seller_receivable_breakdown"]["paypal_fee"]["value"]
    """
    logger.info(
        "Capture completed: capture_id=%s custom_id=%s amount=%s %s",
        resource.get("id"),
        resource.get("custom_id"),
        resource.get("amount", {}).get("value"),
        resource.get("amount", {}).get("currency_code"),
    )
    # TODO: Order.objects.filter(custom_id=resource["custom_id"]).update(
    #           status=Order.Status.PAID, paypal_capture_id=resource["id"])
    # TODO: send_confirmation_email(order)


@register("PAYMENT.CAPTURE.DENIED")
def _on_capture_denied(resource: dict, raw_event: dict) -> None:
    """Payment was declined by the buyer's bank or PayPal risk engine."""
    logger.warning("Capture denied: %s", resource.get("id"))
    # TODO: mark order FAILED, notify user


@register("PAYMENT.CAPTURE.REFUNDED")
def _on_capture_refunded(resource: dict, raw_event: dict) -> None:
    """A refund has been issued (full or partial)."""
    logger.info(
        "Capture refunded: refund_id=%s amount=%s %s",
        resource.get("id"),
        resource.get("amount", {}).get("value"),
        resource.get("amount", {}).get("currency_code"),
    )
    # TODO: update Refund model, notify user


@register("PAYMENT.CAPTURE.REVERSED")
def _on_capture_reversed(resource: dict, raw_event: dict) -> None:
    """Capture reversed via chargeback or dispute."""
    logger.warning("Capture reversed: %s", resource.get("id"))


@register("CHECKOUT.ORDER.APPROVED")
def _on_order_approved(resource: dict, raw_event: dict) -> None:
    """Buyer approved the order on PayPal's site."""
    logger.info("Order approved: %s", resource.get("id"))


@register("PAYMENT.AUTHORIZATION.CREATED")
def _on_authorization_created(resource: dict, raw_event: dict) -> None:
    """Authorization created (intent=AUTHORIZE). You have 29 days to capture."""
    logger.info("Authorization created: %s", resource.get("id"))


@register("PAYMENT.AUTHORIZATION.VOIDED")
def _on_authorization_voided(resource: dict, raw_event: dict) -> None:
    logger.info("Authorization voided: %s", resource.get("id"))


@register("CUSTOMER.DISPUTE.CREATED")
def _on_dispute_created(resource: dict, raw_event: dict) -> None:
    """A buyer has opened a dispute — alert your operations team immediately."""
    logger.warning(
        "Dispute opened: dispute_id=%s reason=%s",
        resource.get("dispute_id"),
        resource.get("reason"),
    )
    # TODO: alert ops, freeze fulfilment for linked order
