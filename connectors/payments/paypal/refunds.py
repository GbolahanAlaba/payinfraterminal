import logging
import uuid
from typing import Any, Dict, Optional

from .base import PayPalAPIClient
from .exceptions import PayPalValidationException

logger = logging.getLogger(__name__)


class PayPalRefunds(PayPalAPIClient):
    """
    Handle PayPal refund operations.

    Mirrors FlutterwaveTransfers in structural role — a focused module
    for money-out operations that inherits PayPalAPIClient.
    """

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        logger.info(
            "Initializing PayPalRefunds - Client ID Prefix: %s, Is Sandbox: %s",
            client_id[:6] if client_id else "INVALID",
            is_sandbox,
        )
        super().__init__(client_id, client_secret, is_sandbox)

    def refund_capture(
        self,
        capture_id: str,
        amount: Optional[str] = None,
        currency: Optional[str] = None,
        note_to_payer: Optional[str] = None,
        invoice_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Refund a captured payment (full or partial).

        Args:
            capture_id:    The PayPal capture ID to refund (from a captured order).
            amount:        Refund amount as a string (major units). Pass None for a
                           full refund.
            currency:      ISO 4217 currency code. Required if amount is specified.
            note_to_payer: Optional note shown to the buyer (max 255 chars).
            invoice_id:    Optional merchant-facing invoice ID for the refund.

        Returns:
            PayPal refund resource dict with id, status, amount, links, etc.
        """
        if not capture_id:
            raise PayPalValidationException("capture_id is required for refund")

        payload: Dict[str, Any] = {}

        if amount:
            if not currency:
                raise PayPalValidationException(
                    "currency is required when specifying a partial refund amount"
                )
            payload["amount"] = {
                "value": str(amount),
                "currency_code": currency.upper(),
            }

        if note_to_payer:
            payload["note_to_payer"] = note_to_payer[:255]

        if invoice_id:
            payload["invoice_id"] = invoice_id

        logger.info(
            "PayPal refund - capture_id=%s amount=%s %s",
            capture_id,
            amount or "FULL",
            currency or "",
        )

        idempotency_key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"refund:{capture_id}:{amount}"))

        return self.post(
            f"/v2/payments/captures/{capture_id}/refund",
            data=payload,
            idempotency_key=idempotency_key,
            prefer_representation=True,
        )

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        """
        Fetch an existing refund by its ID.

        Args:
            refund_id: The PayPal refund ID.

        Returns:
            PayPal refund resource dict.
        """
        if not refund_id:
            raise PayPalValidationException("refund_id is required")
        logger.info("Fetching PayPal refund - Refund ID: %s", refund_id)
        return self.get(f"/v2/payments/refunds/{refund_id}")

    def void_authorization(self, authorization_id: str) -> Dict[str, Any]:
        """
        Void an open authorization, releasing the buyer's held funds.

        Args:
            authorization_id: The PayPal authorization ID to void.

        Returns:
            Empty dict on success (204 No Content from PayPal).
        """
        if not authorization_id:
            raise PayPalValidationException("authorization_id is required")
        logger.info(
            "Voiding PayPal authorization - Authorization ID: %s", authorization_id
        )
        return self.post(
            f"/v2/payments/authorizations/{authorization_id}/void",
            data={},
        )
