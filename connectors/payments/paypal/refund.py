"""
PayPal refund module.

Handles full and partial refunds against captured payments.
"""
from __future__ import annotations

import logging

from .base import Money, PayPalBase

logger = logging.getLogger(__name__)


class PayPalRefund(PayPalBase):
    """Refunds API (v2/payments/captures/{id}/refund)."""

    def refund_capture(
        self,
        capture_id: str,
        amount: Money | None = None,
        note_to_payer: str = "",
        invoice_id: str = "",
    ) -> dict:
        """
        Issue a refund against a completed capture.

        Args:
            capture_id:     The PayPal capture ID to refund.
            amount:         Omit for a full refund; provide for a partial refund.
            note_to_payer:  Message shown to the buyer (max 255 chars).
            invoice_id:     Your internal reference, useful for reconciliation.

        Returns:
            PayPal refund object with ``id`` and ``status``.
        """
        payload: dict = {}
        if amount:
            payload["amount"] = amount.as_dict()
        if note_to_payer:
            payload["note_to_payer"] = note_to_payer[:255]
        if invoice_id:
            payload["invoice_id"] = invoice_id

        logger.info(
            "Refunding capture %s amount=%s note=%r",
            capture_id, amount, note_to_payer[:40] if note_to_payer else "",
        )
        return self._request(
            "POST",
            f"/v2/payments/captures/{capture_id}/refund",
            json=payload,
        )

    def get_refund(self, refund_id: str) -> dict:
        """Fetch a refund by its PayPal refund ID."""
        return self._request("GET", f"/v2/payments/refunds/{refund_id}")
