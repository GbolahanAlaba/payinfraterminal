import logging
from typing import Any, Dict, Optional

from .base import FlutterwaveAPIClient
from .exceptions import FlutterwaveValidationException

logger = logging.getLogger(__name__)


class FlutterwavePayments(FlutterwaveAPIClient):
    """Handle Flutterwave standard payment operations."""

    def __init__(self, secret_key: str, is_sandbox: bool = True):
        logger.info(
            "Initializing FlutterwavePayments - Secret Key Length: %s, Is Sandbox: %s",
            len(secret_key) if secret_key else 0,
            is_sandbox,
        )
        super().__init__(secret_key, is_sandbox)

    def create_payment(
        self,
        tx_ref: str,
        amount: str,
        currency: str,
        redirect_url: str,
        customer: Dict[str, Any],
        customizations: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        payment_options: Optional[str] = None,
        subaccounts: Optional[list[Dict[str, Any]]] = None,
        payment_plan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Flutterwave hosted payment.

        Args:
            tx_ref: Unique transaction reference
            amount: Amount in major units as string
            currency: Currency code (e.g. NGN)
            redirect_url: URL to redirect to after payment
            customer: Customer information (requires email and name)
            customizations: Customization details for checkout
            meta: Additional metadata
            payment_options: Comma separated list of payment options
            subaccounts: List of subaccounts for split payments
            payment_plan: Payment plan identifier
        """
        if not tx_ref:
            raise FlutterwaveValidationException("Transaction reference is required")

        if not redirect_url:
            raise FlutterwaveValidationException("Redirect URL is required")

        if not customer or not customer.get("email"):
            raise FlutterwaveValidationException("Customer email is required")

        payload: Dict[str, Any] = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": currency.upper(),
            "redirect_url": redirect_url,
            "customer": customer,
        }

        if customizations:
            payload["customizations"] = customizations

        if meta:
            payload["meta"] = meta

        if payment_options:
            payload["payment_options"] = payment_options

        if subaccounts:
            payload["subaccounts"] = subaccounts

        if payment_plan:
            payload["payment_plan"] = payment_plan

        logger.info("Creating Flutterwave payment - Payload: %s", payload)
        return self.post("/v3/payments", data=payload)

    def verify_payment_by_reference(self, tx_ref: str) -> Dict[str, Any]:
        """
        Verify a payment using its transaction reference.

        Args:
            tx_ref: Transaction reference used during initialization
        """
        if not tx_ref:
            raise FlutterwaveValidationException(
                "Transaction reference is required for verification",
            )

        logger.info("Verifying Flutterwave payment - Reference: %s", tx_ref)
        return self.get(
            "/v3/transactions/verify_by_reference",
            params={"tx_ref": tx_ref},
        )
