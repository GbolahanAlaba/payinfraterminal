import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FlutterwaveException(Exception):
    """Base exception for all Flutterwave-related errors."""
    
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
        logger.error(f"FlutterwaveException raised: {message}")


class FlutterwaveAPIException(FlutterwaveException):
    """Exception raised for Flutterwave API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_code = error_code
        
        logger.error(
            f"FlutterwaveAPIException raised: message={message}, "
            f"status_code={status_code}, error_code={error_code}"
        )

    def __str__(self):
        parts = [f"FlutterwaveAPIException: {self.message}"]
        
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
            
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
            
        return " ".join(parts)

    def __repr__(self):
        return (
            f"FlutterwaveAPIException(message={self.message!r}, "
            f"status_code={self.status_code}, error_code={self.error_code!r})"
        )


class FlutterwaveAuthenticationException(FlutterwaveAPIException):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str = "Invalid or missing API credentials", **kwargs):
        super().__init__(message, **kwargs)


class FlutterwaveValidationException(FlutterwaveAPIException):
    """Exception raised for request validation errors."""
    
    def __init__(self, message: str, validation_errors: Optional[Dict] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or {}


class FlutterwaveNotFoundException(FlutterwaveAPIException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, **kwargs)


class FlutterwaveRateLimitException(FlutterwaveAPIException):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class FlutterwaveNetworkException(FlutterwaveException):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str = "Network error occurred", original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception


class FlutterwaveWebhookException(FlutterwaveException):
    """Exception raised for webhook-related errors."""
    
    def __init__(self, message: str = "Webhook processing error", **kwargs):
        super().__init__(message)


def map_api_exception(status_code: int, response_data: Dict[str, Any]) -> FlutterwaveAPIException:
    """
    Map HTTP status codes to appropriate Flutterwave exceptions.
    
    Args:
        status_code: HTTP status code from the API response
        response_data: Response data from the API
        
    Returns:
        Appropriate FlutterwaveAPIException subclass
    """
    message = response_data.get("message", "API request failed")
    error_code = None
    
    # Extract error code if available
    error_info = response_data.get("error", {})
    if isinstance(error_info, dict):
        error_code = error_info.get("code")
    
    # Map status codes to specific exceptions
    if status_code == 401:
        return FlutterwaveAuthenticationException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code
        )
    elif status_code == 400:
        validation_errors = response_data.get("errors", {})
        return FlutterwaveValidationException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
            validation_errors=validation_errors
        )
    elif status_code == 404:
        return FlutterwaveNotFoundException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code
        )
    elif status_code == 429:
        retry_after = response_data.get("retry_after")
        return FlutterwaveRateLimitException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code,
            retry_after=retry_after
        )
    else:
        return FlutterwaveAPIException(
            message=message,
            status_code=status_code,
            response_data=response_data,
            error_code=error_code
        )