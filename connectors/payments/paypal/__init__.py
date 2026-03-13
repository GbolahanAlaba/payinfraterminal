"""
PayPal REST API Integration

This package provides a complete integration with PayPal's Orders v2 API,
matching the exact structure of the flutterwave/ and paystack/ connectors
so it slots directly into the payment orchestration platform.

Main Components:
    PayPalClient:                 Main client — exposes .payments and .refunds
    PayPalPayments:               Create orders, verify, capture, authorize
    PayPalRefunds:                Refund captures, void authorizations
    PayPalAPIException:           Exception hierarchy for error handling

Usage:
    from connectors.payments.paypal import PayPalClient

    client = PayPalClient(
        client_id="AXxx...",
        client_secret="EKxx...",
        is_sandbox=True,
    )

    # Create a payment order
    order = client.payments.create_payment(
        tx_ref="greatman009",
        amount="80.00",
        currency="USD",
        redirect_url="https://payflow.com/payments/",
        customer={"email": "customer@example.com"},
    )

    # Get the approval URL to redirect the buyer
    approve_url = next(
        link["href"] for link in order["links"] if link["rel"] == "approve"
    )
"""

from .paypal import PayPalClient
from .payments import PayPalPayments
from .refunds import PayPalRefunds
from .exceptions import (
    PayPalException,
    PayPalAPIException,
    PayPalAuthenticationException,
    PayPalValidationException,
    PayPalNotFoundException,
    PayPalRateLimitException,
    PayPalNetworkException,
    PayPalWebhookException,
)

__all__ = [
    "PayPalClient",
    "PayPalPayments",
    "PayPalRefunds",
    "PayPalException",
    "PayPalAPIException",
    "PayPalAuthenticationException",
    "PayPalValidationException",
    "PayPalNotFoundException",
    "PayPalRateLimitException",
    "PayPalNetworkException",
    "PayPalWebhookException",
]

__version__ = "1.0.0"
