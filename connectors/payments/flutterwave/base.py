import requests
import uuid
import logging
from typing import Dict, Any, Optional

from .exceptions import (
    FlutterwaveAPIException,
    FlutterwaveNetworkException,
    map_api_exception
)

# Set up logging
logger = logging.getLogger(__name__)

class FlutterwaveAPIClient:
    """Base client for Flutterwave API operations."""

    def __init__(self, secret_key: str, is_sandbox: bool = True):
        """
        Initialize the Flutterwave API client.

        Args:
            secret_key: Flutterwave secret key
            is_sandbox: Whether to use sandbox environment
        """
        self.secret_key = secret_key
        self.is_sandbox = is_sandbox
        
        # Flutterwave uses the same base domain for both sandbox (test keys) and live (live keys).
        # The environment is determined by the API keys supplied.
        self.base_url = "https://api.flutterwave.com"

    def _get_headers(self, idempotency_key: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate headers for API requests.

        Args:
            idempotency_key: Optional idempotency key for preventing duplicate requests
            trace_id: Optional trace ID for request tracking

        Returns:
            Dictionary of headers
        """
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key

        if trace_id:
            headers["X-Trace-Id"] = trace_id

        return headers

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None, 
        params: Optional[Dict] = None,
        idempotency_key: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Flutterwave API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            idempotency_key: Optional idempotency key
            trace_id: Optional trace ID

        Returns:
            Response data as dictionary

        Raises:
            FlutterwaveAPIException: If API request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(idempotency_key, trace_id)

        # Log request details
        masked_secret_key = self.secret_key[:6] + "..." + self.secret_key[-4:] if len(self.secret_key) > 10 else "INVALID_KEY"
        logger.info(f"Flutterwave API Request - Method: {method}, URL: {url}")
        logger.info(f"Flutterwave API Request - Headers: {{'Authorization': 'Bearer {masked_secret_key}', 'Content-Type': '{headers.get('Content-Type')}'}}")
        logger.info(f"Flutterwave API Request - Params: {params}")
        logger.info(f"Flutterwave API Request - Data: {data}")
        logger.info(f"Flutterwave API Request - Idempotency Key: {idempotency_key}")
        logger.info(f"Flutterwave API Request - Trace ID: {trace_id}")
        logger.info(f"Flutterwave API Request - Is Sandbox: {self.is_sandbox}")
        logger.info(f"Flutterwave API Request - Base URL: {self.base_url}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )

            # Log response details
            logger.info(f"Flutterwave API Response - Status Code: {response.status_code}")
            logger.info(f"Flutterwave API Response - Headers: {dict(response.headers)}")
            
            # Parse response
            try:
                response_data = response.json()
                logger.info(f"Flutterwave API Response - Body: {response_data}")
            except ValueError:
                logger.error(f"Flutterwave API Response - Invalid JSON: {response.text}")
                raise FlutterwaveAPIException(
                    f"Invalid JSON response: {response.text}",
                    response.status_code
                )

            # Check for successful response
            if response.status_code in [200, 201]:
                if response_data.get("status") == "success":
                    logger.info("Flutterwave API Request Successful")
                    return response_data
                else:
                    # API returned success status code but status field is not success
                    logger.error(f"Flutterwave API Request Failed - Response: {response_data}")
                    raise FlutterwaveAPIException(
                        response_data.get("message", "API request failed"),
                        response.status_code,
                        response_data
                    )
            else:
                # HTTP error status code - use exception mapping
                logger.error(f"Flutterwave API Request Failed - Status Code: {response.status_code}, Response: {response_data}")
                raise map_api_exception(response.status_code, response_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Flutterwave API Network Error: {str(e)}")
            raise FlutterwaveNetworkException(f"Network error: {str(e)}", original_exception=e)

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        # Generate idempotency key if not provided for POST requests
        if "idempotency_key" not in kwargs:
            kwargs["idempotency_key"] = str(uuid.uuid4())
        return self._make_request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
