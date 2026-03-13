import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PayPalException(Exception):
    """Base exception for all PayPal-related errors."""

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
        logger.error(f"PayPalException raised: {message}")


class PayPalAPIException(PayPalException):
    """Exception raised for PayPal API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_code = error_code

        logger.error(
            f"PayPalAPIException raised: message={message}, "
            f"status_code={status_code}, error_code={error_code}"
        )

    def __str__(self):
        parts = [f"PayPalAPIException: {self.message}"]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        return " ".join(parts)

    def __repr__(self):
        return (
            f"PayPalAPIException(message={self.message!r}, "
            f"status_code={self.status_code}, error_code={self.error_code!r})"
        )


class PayPalAuthenticationException(PayPalAPIException):
    """Exception raised for OAuth2 token / credential errors."""

    def __init__(self, message: str = "Invalid or missing PayPal credentials", **kwargs):
        super().__init__(message, **kwargs)


class PayPalValidationException(PayPalAPIException):
    """Exception raised for request validation errors."""

    def __init__(self, message: str, validation_errors: Optional[Dict] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or {}


class PayPalNotFoundException(PayPalAPIException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, **kwargs)


class PayPalRateLimitException(PayPalAPIException):
    """Exception raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "PayPal API rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class PayPalNetworkException(PayPalException):
    """Exception raised for network-related errors."""

    def __init__(
        self,
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.original_exception = original_exception


class PayPalWebhookException(PayPalException):
    """Exception raised for webhook-related errors."""

    def __init__(self, message: str = "Webhook processing error", **kwargs):
        super().__init__(message)


def map_api_exception(status_code: int, response_data: Dict[str, Any]) -> PayPalAPIException:
    """
    Map HTTP status codes to appropriate PayPal exception subclasses.

    Args:
        status_code:   HTTP status code from the PayPal response.
        response_data: Parsed JSON body from the response.

    Returns:
        Appropriate PayPalAPIException subclass instance.
    """
    # PayPal uses 'message' for human-readable errors and 'name' for machine-readable codes
    message = response_data.get("message") or response_data.get("error_description", "API request failed")
    error_code = response_data.get("name") or response_data.get("error")

    if status_code == 401:
        return PayPalAuthenticationException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
        )
    elif status_code == 400:
        validation_errors = response_data.get("details", {})
        return PayPalValidationException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
            validation_errors=validation_errors,
        )
    elif status_code == 404:
        return PayPalNotFoundException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
        )
    elif status_code == 429:
        return PayPalRateLimitException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
        )
    else:
        return PayPalAPIException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
        )
