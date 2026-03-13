import logging
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings

from connectors.payments.providers.base import BasePaymentProvider
from connectors.payments.paypal import PayPalClient
from connectors.payments.paypal.exceptions import PayPalAPIException

logger = logging.getLogger(__name__)


class PayPalProvider(BasePaymentProvider):
    """
    PayPal Payment Provider Implementation.

    Mirrors FlutterwaveProvider exactly so it slots into PaymentService /
    PaymentRouteEngine with zero changes to existing orchestration code.

    The credential stored in ClientProviderCredential for PayPal must be JSON:
        {
            "client_id":     "AXxx...",
            "client_secret": "EKxx..."
        }

    Because PayPal uses a client_id + client_secret pair instead of a single
    secret_key, the provider unpacks them from the stored credentials dict.
    The routing engine currently passes a single `secret_key` string, so we
    support two calling conventions:

        1. secret_key is a JSON string:  '{"client_id": "...", "client_secret": "..."}'
        2. secret_key is a pipe-delimited string: "client_id|client_secret"

    Both are parsed transparently so the routing engine requires no changes.
    """

    def __init__(self, secret_key: str, callback_url: str = None):
        """
        Args:
            secret_key:    PayPal credentials encoded as JSON or pipe-delimited
                           "client_id|client_secret" string.
            callback_url:  Return URL after buyer approves / cancels on PayPal.
        """
        if not secret_key:
            raise ValueError("PayPal credentials (secret_key) are required.")

        # ------------------------------------------------------------------
        # Parse client_id / client_secret from the encoded secret_key
        # ------------------------------------------------------------------
        client_id, client_secret = self._parse_credentials(secret_key)

        paypal_settings = getattr(settings, "PAYMENT_PROVIDER", {}).get("PAYPAL", {})
        default_callback = paypal_settings.get("callback_url")

        self.callback_url = callback_url or default_callback

        if not self.callback_url:
            raise ValueError("PayPal callback_url must be configured.")

        self.client_id = client_id
        self.client_secret = client_secret

        # Sandbox detection: PayPal sandbox client IDs start with "AX" when using
        # test credentials, but the most reliable signal is an explicit setting.
        paypal_env = paypal_settings.get("environment", "sandbox").lower()
        self.is_sandbox = paypal_env != "live"

        super().__init__(
            api_client=PayPalClient(
                client_id=client_id,
                client_secret=client_secret,
                is_sandbox=self.is_sandbox,
            )
        )
        self.name = "paypal"

    # ------------------------------------------------------------------
    # Credential parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_credentials(secret_key: str):
        """
        Extract (client_id, client_secret) from secret_key.

        Supports:
          - JSON string: '{"client_id": "AX...", "client_secret": "EK..."}'
          - Pipe-delimited: "AX...|EK..."
          - Direct client_id only (legacy, will raise)
        """
        import json

        secret_key = secret_key.strip()

        # Try JSON first
        if secret_key.startswith("{"):
            try:
                data = json.loads(secret_key)
                client_id = data.get("client_id") or data.get("PAYPAL_CLIENT_ID")
                client_secret = data.get("client_secret") or data.get("PAYPAL_CLIENT_SECRET")
                if client_id and client_secret:
                    return client_id, client_secret
            except json.JSONDecodeError:
                pass

        # Try pipe-delimited
        if "|" in secret_key:
            parts = secret_key.split("|", 1)
            if len(parts) == 2 and parts[0] and parts[1]:
                return parts[0].strip(), parts[1].strip()

        raise ValueError(
            "PayPal secret_key must be a JSON string "
            '\'{"client_id": "...", "client_secret": "..."}\' '
            "or pipe-delimited 'client_id|client_secret'."
        )

    # ------------------------------------------------------------------
    # initialize_transaction — mirrors FlutterwaveProvider
    # ------------------------------------------------------------------

    def initialize_transaction(
        self,
        email: str,
        amount: int,
        currency: str = "USD",
        reference: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Initialize a PayPal payment (create an order + return approval URL).

        Args:
            email:     Customer email address.
            amount:    Amount in minor units (e.g. cents for USD). Will be
                       converted to major units (dollars) before sending to PayPal.
            currency:  ISO 4217 currency code. Defaults to "USD".
                       PayPal does not support NGN — use USD or another supported
                       currency. The orchestration layer passes whatever currency
                       the merchant configured.
            reference: Optional idempotent transaction reference.
            **kwargs:  Forwarded fields: callback_url, name, metadata, etc.

        Returns:
            Raw PayPal order response. clean_init_data() normalises this into
            the unified response shape expected by PaymentService._unify_response().
        """
        try:
            # Convert minor → major units (same logic as FlutterwaveProvider)
            amount_decimal = (Decimal(amount) / 100).quantize(Decimal("0.01"))
            amount_str = format(amount_decimal, "f")

            redirect_url = kwargs.get("callback_url") or self.callback_url
            if not redirect_url:
                raise ValueError("redirect_url / callback_url is required for PayPal payments.")

            tx_ref = reference or uuid.uuid4().hex[:12].upper()

            customer_data = {"email": email}
            if kwargs.get("name"):
                customer_data["name"] = kwargs["name"]

            metadata = {"customer_email": email, "source": "payinfra_backend"}
            if kwargs.get("metadata"):
                metadata.update(kwargs["metadata"])
            # Strip None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            payment_response = self.api_client.payments.create_payment(
                tx_ref=tx_ref,
                amount=amount_str,
                currency=currency.upper(),
                redirect_url=redirect_url,
                customer=customer_data,
                cancel_url=kwargs.get("cancel_url") or redirect_url,
                meta=metadata or None,
                brand_name=kwargs.get("brand_name", "PayInfra"),
            )

            # Inject tx_ref and helpers into the response data block so that
            # clean_init_data / _unify_response can find them — same pattern as
            # FlutterwaveProvider.initialize_transaction().
            payment_response.setdefault("data", {})
            payment_response["data"].update(
                {
                    "tx_ref": tx_ref,
                    "amount": amount_str,
                    "currency": currency.upper(),
                    "redirect_url": redirect_url,
                }
            )

            return payment_response

        except PayPalAPIException as exc:
            logger.error("PayPalAPIException during transaction initialization: %s", exc)
            logger.error(
                "Exception details - Status Code: %s, Error Code: %s, Response Data: %s",
                exc.status_code, exc.error_code, exc.response_data,
            )
            return {
                "status": "error",
                "message": str(exc),
                "error": {
                    "code": exc.error_code,
                    "status_code": exc.status_code,
                },
            }
        except Exception as exc:
            logger.error(
                "Unexpected error during PayPal transaction initialization: %s",
                exc, exc_info=True,
            )
            return {"status": "error", "message": f"Unexpected error: {exc}"}

    # ------------------------------------------------------------------
    # verify_transaction — mirrors FlutterwaveProvider
    # ------------------------------------------------------------------

    def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify a PayPal payment by fetching the order.

        Args:
            transaction_id: The PayPal order ID (stored as reference / access_code
                            in the unified response from initialize_transaction).

        Returns:
            Raw PayPal order object.
        """
        try:
            return self.api_client.payments.verify_payment_by_reference(transaction_id)
        except PayPalAPIException as exc:
            logger.error("PayPalAPIException during transaction verification: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "error": {"code": exc.error_code, "status_code": exc.status_code},
            }
        except Exception as exc:
            logger.error(
                "Unexpected error during PayPal transaction verification: %s",
                exc, exc_info=True,
            )
            return {"status": "error", "message": f"Verification failed: {exc}"}

    # ------------------------------------------------------------------
    # clean_init_data — mirrors FlutterwaveProvider / PaystackProvider
    # ------------------------------------------------------------------

    def clean_init_data(self, init_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise the raw PayPal order response into the unified shape that
        PaymentService._unify_response() expects.

        PayPal order status is "CREATED" on success (not "success"), so we
        map it to "success" for consistency with Paystack / Flutterwave.

        The payment_url (approval link) lives in init_data["links"] as the
        entry with rel == "approve".

        Returns a dict with: payment_url, access_code, reference, amount,
        currency, status, provider — identical to FlutterwaveProvider.clean_init_data().
        """
        # PayPal returns {"id": "...", "status": "CREATED", "links": [...]}
        # On error we return {"status": "error", "message": "..."}
        if init_data.get("status") == "error":
            return {
                "error": True,
                "message": init_data.get("message", "PayPal transaction initialization failed"),
                "status": "failed",
            }

        paypal_order_id = init_data.get("id")
        links = init_data.get("links", [])
        data_block = init_data.get("data", {})

        # Find the approve link — this is the redirect URL for the buyer
        payment_url = None
        for link in links:
            if link.get("rel") == "approve":
                payment_url = link["href"]
                break

        # Fallback: check data block (injected by initialize_transaction)
        if not payment_url:
            payment_url = data_block.get("payment_url") or data_block.get("redirect_url")

        if not payment_url:
            logger.warning(
                "PayPal initialization returned no approve link. Order ID: %s", paypal_order_id
            )
            return {
                "error": True,
                "message": "Payment approval link not returned by PayPal.",
                "status": "failed",
            }

        tx_ref = data_block.get("tx_ref") or paypal_order_id

        cleaned = {
            # Standard unified fields
            "payment_url": payment_url,
            "access_code": paypal_order_id,     # PayPal order ID = access code
            "reference": tx_ref,                # Our tx_ref = reference
            "amount": data_block.get("amount"),
            "currency": data_block.get("currency"),
            "metadata": {},
            "status": "success",                # Map CREATED → success
            "provider": "paypal",
            # PayPal-specific extras (available to caller via data block)
            "paypal_order_id": paypal_order_id,
        }

        logger.info("PayPal clean_init_data - Result: %s", cleaned)
        return cleaned

    # ------------------------------------------------------------------
    # process_payment / refund_payment — required by BasePaymentProvider ABC
    # ------------------------------------------------------------------

    def process_payment(
        self, amount: float, currency: str, customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Thin wrapper around initialize_transaction for ABC compatibility."""
        email = customer_info.get("email", "")
        return self.initialize_transaction(
            email=email,
            amount=int(amount * 100),
            currency=currency,
            name=customer_info.get("name"),
        )

    def refund_payment(
        self, transaction_id: str, amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Refund a captured PayPal payment.

        Note: transaction_id here should be the PayPal *capture ID* (not the
        order ID). After capture_order() the capture ID is available in:
            response["purchase_units"][0]["payments"]["captures"][0]["id"]

        Args:
            transaction_id: PayPal capture ID.
            amount:         Amount to refund in major units. None = full refund.

        Returns:
            PayPal refund resource dict, or error dict on failure.
        """
        try:
            # Determine currency from settings or default to USD
            paypal_settings = getattr(settings, "PAYMENT_PROVIDER", {}).get("PAYPAL", {})
            default_currency = paypal_settings.get("default_currency", "USD")

            amount_str = format(Decimal(str(amount)).quantize(Decimal("0.01")), "f") if amount else None
            return self.api_client.refunds.refund_capture(
                capture_id=transaction_id,
                amount=amount_str,
                currency=default_currency if amount_str else None,
            )
        except PayPalAPIException as exc:
            logger.error("PayPalAPIException during refund: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "error": {"code": exc.error_code, "status_code": exc.status_code},
            }
        except Exception as exc:
            logger.error("Unexpected error during PayPal refund: %s", exc, exc_info=True)
            return {"status": "error", "message": f"Refund failed: {exc}"}
