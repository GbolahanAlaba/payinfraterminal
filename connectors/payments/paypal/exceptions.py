"""
PayPal exception hierarchy.
Import from here everywhere — never from base.py directly.
"""
from __future__ import annotations


class PayPalError(Exception):
    """Base exception for all PayPal errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status_code}, message={self})"


class PayPalAuthError(PayPalError):
    """OAuth2 token acquisition or validation failed."""


class PayPalOrderError(PayPalError):
    """Order creation, capture, or authorization failed."""


class PayPalTransactionError(PayPalError):
    """Generic transaction-level failure."""


class PayPalRefundError(PayPalError):
    """Refund request failed."""


class PayPalWebhookError(PayPalError):
    """Webhook signature verification failed or is misconfigured."""


class PayPalRetryableError(PayPalError):
    """Transient server-side error — safe to retry with back-off."""
