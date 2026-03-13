import logging
import time
import uuid
from typing import Dict, Any, Optional

import requests
from django.core.cache import cache

from .exceptions import (
    PayPalAPIException,
    PayPalAuthenticationException,
    PayPalNetworkException,
    PayPalRateLimitException,
    map_api_exception,
)

logger = logging.getLogger(__name__)

_SANDBOX_BASE_URL = "https://api-m.sandbox.paypal.com"
_LIVE_BASE_URL = "https://api-m.paypal.com"

_TOKEN_CACHE_KEY_PREFIX = "paypal_oauth_token"
_TOKEN_EXPIRY_BUFFER_SECS = 60   # refresh 60s before actual expiry
_MAX_RETRIES = 3


class PayPalAPIClient:
    """
    Base HTTP client for PayPal REST API operations.

    Mirrors FlutterwaveAPIClient structure:
      - __init__(client_id, client_secret, is_sandbox)
      - _get_headers()
      - _make_request()
      - get() / post() / put() / delete()

    Additional PayPal-specific concerns handled here:
      - OAuth2 client-credentials token lifecycle (cached via Django cache)
      - Automatic token refresh on 401
      - Exponential-backoff retry on transient errors (429 / 503 / 504)
    """

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        """
        Initialize the PayPal API client.

        Args:
            client_id:     PayPal REST app Client ID.
            client_secret: PayPal REST app Client Secret.
            is_sandbox:    True  → sandbox environment.
                           False → live/production environment.
        """
        if not client_id or not client_secret:
            raise ValueError("PayPal client_id and client_secret are required.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox
        self.base_url = _SANDBOX_BASE_URL if is_sandbox else _LIVE_BASE_URL

    # ------------------------------------------------------------------
    # OAuth2 token management
    # ------------------------------------------------------------------

    @property
    def _token_cache_key(self) -> str:
        """Per-client cache key so different merchants don't share tokens."""
        return f"{_TOKEN_CACHE_KEY_PREFIX}:{self.client_id[:12]}"

    def _fetch_access_token(self) -> str:
        """
        Obtain a fresh OAuth2 client-credentials token from PayPal and cache it.

        Raises:
            PayPalAuthenticationException: If token acquisition fails.
            PayPalNetworkException:        On network-level errors.
        """
        logger.info(
            "PayPal: requesting new OAuth2 token (sandbox=%s, client_prefix=%s)",
            self.is_sandbox,
            self.client_id[:6],
        )
        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            raise PayPalNetworkException(
                f"Token request network error: {exc}", original_exception=exc
            )

        if response.status_code != 200:
            try:
                err_data = response.json()
            except Exception:
                err_data = {"raw": response.text[:200]}
            raise PayPalAuthenticationException(
                "Failed to obtain PayPal access token",
                status_code=response.status_code,
                response_data=err_data,
            )

        data = response.json()
        token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        ttl = max(expires_in - _TOKEN_EXPIRY_BUFFER_SECS, 0)
        cache.set(self._token_cache_key, token, timeout=ttl)
        logger.debug("PayPal OAuth2 token cached for %ds", ttl)
        return token

    def _get_access_token(self) -> str:
        """Return cached token or fetch a new one."""
        token = cache.get(self._token_cache_key)
        if token:
            return token
        return self._fetch_access_token()

    def _invalidate_token(self) -> None:
        """Bust the cached token (called on 401 to force re-auth)."""
        cache.delete(self._token_cache_key)
        logger.warning("PayPal: token cache invalidated (will re-fetch on next request)")

    # ------------------------------------------------------------------
    # Headers
    # ------------------------------------------------------------------

    def _get_headers(
        self,
        idempotency_key: Optional[str] = None,
        prefer_representation: bool = False,
    ) -> Dict[str, str]:
        """
        Generate headers for API requests.

        Args:
            idempotency_key:        Maps to 'PayPal-Request-Id' header.
            prefer_representation:  If True, adds 'Prefer: return=representation'
                                    so PayPal returns the full resource body.

        Returns:
            Dictionary of headers.
        """
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["PayPal-Request-Id"] = idempotency_key
        if prefer_representation:
            headers["Prefer"] = "return=representation"
        return headers

    # ------------------------------------------------------------------
    # Core request method
    # ------------------------------------------------------------------

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        idempotency_key: Optional[str] = None,
        prefer_representation: bool = False,
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to the PayPal API.

        Args:
            method:                 HTTP method (GET, POST, PATCH, DELETE).
            endpoint:               Path relative to base_url (e.g. /v2/checkout/orders).
            data:                   JSON request body.
            params:                 URL query parameters.
            idempotency_key:        Optional PayPal-Request-Id for safe retries.
            prefer_representation:  Whether to add Prefer: return=representation.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            PayPalAPIException subclass on failure.
        """
        url = f"{self.base_url}{endpoint}"
        masked_client_id = (
            self.client_id[:6] + "..." + self.client_id[-4:]
            if len(self.client_id) > 10
            else "INVALID_ID"
        )

        logger.info("PayPal API Request - Method: %s, URL: %s", method, url)
        logger.info(
            "PayPal API Request - Client: %s | Sandbox: %s | Idempotency: %s",
            masked_client_id,
            self.is_sandbox,
            idempotency_key,
        )
        logger.info("PayPal API Request - Params: %s", params)
        logger.info("PayPal API Request - Data: %s", data)

        last_exception: Optional[Exception] = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                headers = self._get_headers(idempotency_key, prefer_representation)
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=30,
                )

                logger.info("PayPal API Response - Status Code: %s", response.status_code)
                logger.info("PayPal API Response - Headers: %s", dict(response.headers))

                # 204 No Content (e.g. void authorization)
                if response.status_code == 204:
                    logger.info("PayPal API Request Successful (204 No Content)")
                    return {}

                try:
                    response_data = response.json()
                    logger.info("PayPal API Response - Body: %s", response_data)
                except ValueError:
                    logger.error("PayPal API Response - Invalid JSON: %s", response.text)
                    raise PayPalAPIException(
                        f"Invalid JSON response: {response.text[:200]}",
                        response.status_code,
                    )

                # Success
                if response.status_code in (200, 201):
                    logger.info("PayPal API Request Successful")
                    return response_data

                # Transient errors — retry with exponential backoff
                if response.status_code in (429, 503, 504):
                    wait_secs = 2 ** (attempt - 1)
                    logger.warning(
                        "PayPal transient error %d (attempt %d/%d) — retrying in %ds",
                        response.status_code, attempt, _MAX_RETRIES, wait_secs,
                    )
                    last_exception = PayPalRateLimitException(
                        f"PayPal transient error {response.status_code}",
                        status_code=response.status_code,
                        response_data=response_data,
                    )
                    time.sleep(wait_secs)
                    continue

                # 401 — invalidate cached token and retry once
                if response.status_code == 401 and attempt == 1:
                    logger.warning("PayPal 401 received — invalidating token cache and retrying")
                    self._invalidate_token()
                    continue

                # All other errors
                logger.error(
                    "PayPal API Request Failed - Status Code: %d, Response: %s",
                    response.status_code, response_data,
                )
                raise map_api_exception(response.status_code, response_data)

            except requests.exceptions.RequestException as exc:
                logger.error("PayPal API Network Error (attempt %d): %s", attempt, exc)
                last_exception = PayPalNetworkException(
                    f"Network error: {exc}", original_exception=exc
                )
                if attempt < _MAX_RETRIES:
                    time.sleep(2 ** (attempt - 1))
                continue

        raise last_exception  # type: ignore[misc]

    # ------------------------------------------------------------------
    # HTTP convenience methods — mirrors FlutterwaveAPIClient exactly
    # ------------------------------------------------------------------

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        idempotency_key: Optional[str] = None,
        prefer_representation: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make a POST request. Auto-generates idempotency key if not supplied."""
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())
        return self._make_request(
            "POST",
            endpoint,
            data=data,
            idempotency_key=idempotency_key,
            prefer_representation=prefer_representation,
            **kwargs,
        )

    def patch(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
