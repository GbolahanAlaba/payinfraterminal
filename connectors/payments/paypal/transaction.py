"""
PayPal transaction module.

Covers the full Orders v2 lifecycle:
  create → (approve on PayPal) → capture  (intent=CAPTURE)
  create → (approve on PayPal) → authorize → capture_authorization / void  (intent=AUTHORIZE)
"""
from __future__ import annotations

import logging

from .base import Money, OrderRequest, PayPalBase

logger = logging.getLogger(__name__)


class PayPalTransaction(PayPalBase):
    """Orders v2 + Authorizations API."""

    # ------------------------------------------------------------------
    # Order lifecycle
    # ------------------------------------------------------------------

    def create_order(self, order_request: OrderRequest, idempotency_key: str = "") -> dict:
        """
        Create a PayPal order.

        Returns the full order object including the ``approve`` link the
        buyer must visit (or you can pass the order ID to the JS SDK).
        """
        logger.info("Creating PayPal order custom_id=%s", order_request.custom_id)
        return self._request(
            "POST",
            "/v2/checkout/orders",
            json=order_request.build_payload(),
            prefer="return=representation",
            paypal_request_id=idempotency_key or None,
        )

    def get_order(self, paypal_order_id: str) -> dict:
        """Fetch the current state of an order."""
        return self._request("GET", f"/v2/checkout/orders/{paypal_order_id}")

    def capture_order(self, paypal_order_id: str, idempotency_key: str = "") -> dict:
        """
        Capture an approved order (intent=CAPTURE flow).

        Safe to call multiple times with the same ``idempotency_key`` —
        PayPal will return the original response without double-charging.
        """
        logger.info("Capturing PayPal order %s", paypal_order_id)
        return self._request(
            "POST",
            f"/v2/checkout/orders/{paypal_order_id}/capture",
            json={},
            prefer="return=representation",
            paypal_request_id=idempotency_key or None,
        )

    def authorize_order(self, paypal_order_id: str, idempotency_key: str = "") -> dict:
        """
        Authorize an approved order (intent=AUTHORIZE flow).

        Authorization is valid for 29 days; you must capture within that window.
        """
        logger.info("Authorizing PayPal order %s", paypal_order_id)
        return self._request(
            "POST",
            f"/v2/checkout/orders/{paypal_order_id}/authorize",
            json={},
            prefer="return=representation",
            paypal_request_id=idempotency_key or None,
        )

    # ------------------------------------------------------------------
    # Authorization lifecycle (intent=AUTHORIZE)
    # ------------------------------------------------------------------

    def capture_authorization(
        self,
        authorization_id: str,
        amount: Money | None = None,
        final_capture: bool = True,
    ) -> dict:
        """
        Capture a previously authorized payment.

        Pass ``amount`` for a partial capture.
        Set ``final_capture=False`` if you intend to capture again later.
        """
        payload: dict = {}
        if amount:
            payload["amount"] = amount.as_dict()
            payload["final_capture"] = final_capture
        logger.info("Capturing authorization %s (final=%s)", authorization_id, final_capture)
        return self._request(
            "POST",
            f"/v2/payments/authorizations/{authorization_id}/capture",
            json=payload,
        )

    def void_authorization(self, authorization_id: str) -> dict:
        """Void an open authorization, releasing the hold on the buyer's funds."""
        logger.info("Voiding authorization %s", authorization_id)
        return self._request(
            "POST",
            f"/v2/payments/authorizations/{authorization_id}/void",
            json={},
        )

    def get_authorization(self, authorization_id: str) -> dict:
        return self._request("GET", f"/v2/payments/authorizations/{authorization_id}")

    def get_capture(self, capture_id: str) -> dict:
        return self._request("GET", f"/v2/payments/captures/{capture_id}")
