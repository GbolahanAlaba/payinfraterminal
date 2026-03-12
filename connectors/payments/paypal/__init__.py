"""
PayPal integration package.

Public API::

    from paypal import paypal_client
    from paypal.base import Money, OrderItem, OrderRequest
    from paypal.exceptions import PayPalError, PayPalAuthError, PayPalOrderError
    from paypal.webhook import register, dispatch
"""
from .client import PayPalClient, paypal_client
from .base import Money, OrderItem, OrderRequest
from .exceptions import (
    PayPalError,
    PayPalAuthError,
    PayPalOrderError,
    PayPalRefundError,
    PayPalTransactionError,
    PayPalWebhookError,
    PayPalRetryableError,
)
from .webhook import register, dispatch

__all__ = [
    # Client
    "PayPalClient",
    "paypal_client",
    # Data models
    "Money",
    "OrderItem",
    "OrderRequest",
    # Exceptions
    "PayPalError",
    "PayPalAuthError",
    "PayPalOrderError",
    "PayPalRefundError",
    "PayPalTransactionError",
    "PayPalWebhookError",
    "PayPalRetryableError",
    # Webhook
    "register",
    "dispatch",
]
