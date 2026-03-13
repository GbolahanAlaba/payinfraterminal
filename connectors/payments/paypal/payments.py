import logging
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .base import PayPalAPIClient
from .exceptions import PayPalValidationException

logger = logging.getLogger(__name__)


class PayPalPayments(PayPalAPIClient):
    """
    Handle PayPal Orders v2 payment operations.

    Mirrors FlutterwavePayments:
      - __init__(client_id, client_secret, is_sandbox)
      - create_payment(...)   → creates a PayPal order + returns checkout link
      - verify_payment_by_reference(...) → fetches order status by order_id

    PayPal payment lifecycle:
        create_payment  →  buyer approves on PayPal  →  capture_order
    """

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        logger.info(
            "Initializing PayPalPayments - Client ID Prefix: %s, Is Sandbox: %s",
            client_id[:6] if client_id else "INVALID",
            is_sandbox,
        )
        super().__init__(client_id, client_secret, is_sandbox)

    def create_payment(
        self,
        tx_ref: str,
        amount: str,
        currency: str,
        redirect_url: str,
        customer: Dict[str, Any],
        cancel_url: Optional[str] = None,
        intent: str = "CAPTURE",
        items: Optional[List[Dict[str, Any]]] = None,
        meta: Optional[Dict[str, Any]] = None,
        brand_name: str = "PayInfra",
        shipping_preference: str = "NO_SHIPPING",
    ) -> Dict[str, Any]:
        """
        Create a PayPal hosted payment order.

        Maps to FlutterwavePayments.create_payment() — same purpose,
        same argument style. Returns the raw PayPal order response which
        includes the 'approve' link used as payment_url.

        Args:
            tx_ref:               Unique transaction reference (stored as custom_id).
            amount:               Amount as a decimal string (major units, e.g. "80.00").
            currency:             ISO 4217 code (e.g. "USD", "GBP"). PayPal does not
                                  support NGN natively — use USD/EUR or a supported currency.
            redirect_url:         URL PayPal redirects the buyer to after approval.
            customer:             Must contain at least {"email": "..."}.
            cancel_url:           URL PayPal redirects the buyer to on cancellation.
                                  Falls back to redirect_url if not provided.
            intent:               "CAPTURE" (default) charges immediately on capture.
                                  "AUTHORIZE" places a hold for later capture.
            items:                Optional list of line-item dicts for the order breakdown.
            meta:                 Arbitrary metadata stored in the order description.
            brand_name:           Displayed on the PayPal checkout page.
            shipping_preference:  "NO_SHIPPING" | "GET_FROM_FILE" | "SET_PROVIDED_ADDRESS".

        Returns:
            Raw PayPal order response dict. The approve link is at:
            next(l["href"] for l in response["links"] if l["rel"] == "approve")
        """
        if not tx_ref:
            raise PayPalValidationException("Transaction reference (tx_ref) is required")
        if not redirect_url:
            raise PayPalValidationException("redirect_url is required for PayPal payments")
        if not customer or not customer.get("email"):
            raise PayPalValidationException("Customer email is required")

        # Build purchase unit
        purchase_unit: Dict[str, Any] = {
            "reference_id": tx_ref,
            "custom_id": tx_ref,
            "amount": {
                "currency_code": currency.upper(),
                "value": str(amount),
            },
        }

        # Optional line-items breakdown
        if items:
            item_total = sum(
                Decimal(str(i.get("unit_amount", {}).get("value", "0")))
                * int(i.get("quantity", 1))
                for i in items
            )
            purchase_unit["amount"]["breakdown"] = {
                "item_total": {
                    "currency_code": currency.upper(),
                    "value": str(item_total),
                }
            }
            purchase_unit["items"] = items

        if meta:
            purchase_unit["description"] = str(meta)[:127]

        payload: Dict[str, Any] = {
            "intent": intent.upper(),
            "purchase_units": [purchase_unit],
            "application_context": {
                "return_url": redirect_url,
                "cancel_url": cancel_url or redirect_url,
                "shipping_preference": shipping_preference,
                "user_action": "PAY_NOW",
                "brand_name": brand_name,
                "locale": "en-US",
            },
        }

        # Attach payer email if present
        if customer.get("email"):
            payload["payer"] = {"email_address": customer["email"]}

        logger.info(
            "Creating PayPal payment - tx_ref=%s amount=%s %s", tx_ref, amount, currency
        )
        logger.info("Creating PayPal payment - Payload: %s", payload)

        # Use a deterministic idempotency key so duplicate calls for the same
        # tx_ref are safe (idempotent POST)
        idempotency_key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"create:{tx_ref}"))

        return self.post(
            "/v2/checkout/orders",
            data=payload,
            idempotency_key=idempotency_key,
            prefer_representation=True,
        )

    def verify_payment_by_reference(self, order_id: str) -> Dict[str, Any]:
        """
        Verify a payment by fetching the PayPal order.

        Mirrors FlutterwavePayments.verify_payment_by_reference().

        Args:
            order_id: The PayPal order ID returned from create_payment
                      (e.g. "5O190127TN364715T"). This is stored as
                      access_code / reference in the unified response.

        Returns:
            Raw PayPal order object with status, purchase_units, payer, links, etc.
        """
        if not order_id:
            raise PayPalValidationException(
                "order_id is required for PayPal payment verification"
            )
        logger.info("Verifying PayPal payment - Order ID: %s", order_id)
        return self.get(f"/v2/checkout/orders/{order_id}")

    def capture_order(self, order_id: str) -> Dict[str, Any]:
        """
        Capture an approved PayPal order (CAPTURE intent flow).

        Called after the buyer has approved the payment on PayPal and
        been redirected back via redirect_url.

        Args:
            order_id: The PayPal order ID to capture.

        Returns:
            Captured order response with final COMPLETED status.
        """
        if not order_id:
            raise PayPalValidationException("order_id is required for capture")
        logger.info("Capturing PayPal order - Order ID: %s", order_id)
        idempotency_key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"capture:{order_id}"))
        return self.post(
            f"/v2/checkout/orders/{order_id}/capture",
            data={},
            idempotency_key=idempotency_key,
            prefer_representation=True,
        )

    def authorize_order(self, order_id: str) -> Dict[str, Any]:
        """
        Authorize an approved PayPal order (AUTHORIZE intent flow).

        Places a hold on buyer funds without charging immediately.

        Args:
            order_id: The PayPal order ID to authorize.

        Returns:
            Authorized order response.
        """
        if not order_id:
            raise PayPalValidationException("order_id is required for authorization")
        logger.info("Authorizing PayPal order - Order ID: %s", order_id)
        idempotency_key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"authorize:{order_id}"))
        return self.post(
            f"/v2/checkout/orders/{order_id}/authorize",
            data={},
            idempotency_key=idempotency_key,
            prefer_representation=True,
        )
