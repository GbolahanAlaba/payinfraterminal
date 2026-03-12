"""
PayPal base client.

Handles:
  - OAuth2 token lifecycle (cached, auto-refreshed)
  - Authenticated HTTP requests with exponential-backoff retry
  - Response normalisation and error mapping
  - Shared data-model dataclasses (Money, OrderItem, OrderRequest)

All feature modules (transaction, refund, webhook) inherit from PayPalBase.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

import requests
from django.conf import settings
from django.core.cache import cache

from .exceptions import (
    PayPalAuthError,
    PayPalOrderError,
    PayPalRetryableError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums / constants
# ---------------------------------------------------------------------------

class Environment(str, Enum):
    SANDBOX = "sandbox"
    LIVE = "live"


BASE_URLS: dict[Environment, str] = {
    Environment.SANDBOX: "https://api-m.sandbox.paypal.com",
    Environment.LIVE: "https://api-m.paypal.com",
}

TOKEN_CACHE_KEY = "paypal_access_token"
_TOKEN_BUFFER_SECS = 60  # refresh token this many seconds before it expires


# ---------------------------------------------------------------------------
# Shared data models
# ---------------------------------------------------------------------------

@dataclass
class Money:
    currency_code: str
    value: Decimal

    def as_dict(self) -> dict:
        return {"currency_code": self.currency_code, "value": str(self.value)}


@dataclass
class OrderItem:
    name: str
    unit_amount: Money
    quantity: int = 1
    description: str = ""
    sku: str = ""
    category: str = "PHYSICAL_GOODS"  # PHYSICAL_GOODS | DIGITAL_GOODS | DONATION

    def as_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "unit_amount": self.unit_amount.as_dict(),
            "quantity": str(self.quantity),
            "category": self.category,
        }
        if self.description:
            d["description"] = self.description
        if self.sku:
            d["sku"] = self.sku
        return d


@dataclass
class OrderRequest:
    intent: str                   # CAPTURE | AUTHORIZE
    currency_code: str
    total_amount: Decimal
    items: list[OrderItem] = field(default_factory=list)
    reference_id: str = ""
    description: str = ""
    custom_id: str = ""           # maps to your internal order / invoice ID
    invoice_id: str = ""
    return_url: str = ""
    cancel_url: str = ""
    shipping_preference: str = "NO_SHIPPING"  # GET_FROM_FILE | SET_PROVIDED_ADDRESS

    def build_payload(self) -> dict:
        item_total = sum(i.unit_amount.value * i.quantity for i in self.items)

        breakdown: dict = {}
        if self.items:
            breakdown["item_total"] = Money(self.currency_code, item_total).as_dict()

        amount: dict = {
            "currency_code": self.currency_code,
            "value": str(self.total_amount),
        }
        if breakdown:
            amount["breakdown"] = breakdown

        purchase_unit: dict = {"amount": amount}
        if self.reference_id:
            purchase_unit["reference_id"] = self.reference_id
        if self.description:
            purchase_unit["description"] = self.description
        if self.custom_id:
            purchase_unit["custom_id"] = self.custom_id
        if self.invoice_id:
            purchase_unit["invoice_id"] = self.invoice_id
        if self.items:
            purchase_unit["items"] = [i.as_dict() for i in self.items]

        payload: dict = {
            "intent": self.intent,
            "purchase_units": [purchase_unit],
            "application_context": {
                "shipping_preference": self.shipping_preference,
                "user_action": "PAY_NOW",
                "brand_name": getattr(settings, "PAYPAL_BRAND_NAME", ""),
                "locale": "en-US",
            },
        }
        if self.return_url:
            payload["application_context"]["return_url"] = self.return_url
        if self.cancel_url:
            payload["application_context"]["cancel_url"] = self.cancel_url

        return payload


# ---------------------------------------------------------------------------
# Base HTTP client
# ---------------------------------------------------------------------------

class PayPalBase:
    """
    Thread-safe base client.  Configure via Django settings::

        PAYPAL = {
            "CLIENT_ID": "...",
            "CLIENT_SECRET": "...",
            "ENVIRONMENT": "sandbox",   # or "live"
            "WEBHOOK_ID": "...",
            "TIMEOUT": 30,
            "MAX_RETRIES": 3,
        }
    """

    def __init__(self) -> None:
        cfg: dict = getattr(settings, "PAYPAL", {})
        self._client_id: str = cfg["CLIENT_ID"]
        self._client_secret: str = cfg["CLIENT_SECRET"]
        env = Environment(cfg.get("ENVIRONMENT", "sandbox"))
        self._base_url: str = BASE_URLS[env]
        self._webhook_id: str = cfg.get("WEBHOOK_ID", "")
        self._timeout: int = int(cfg.get("TIMEOUT", 30))
        self._max_retries: int = int(cfg.get("MAX_RETRIES", 3))
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        token = cache.get(TOKEN_CACHE_KEY)
        if token:
            return token

        response = self._session.post(
            f"{self._base_url}/v1/oauth2/token",
            auth=(self._client_id, self._client_secret),
            data={"grant_type": "client_credentials"},
            timeout=self._timeout,
        )
        if response.status_code != 200:
            raise PayPalAuthError(
                "Failed to obtain PayPal access token",
                status_code=response.status_code,
                details=self._safe_json(response),
            )

        data = response.json()
        token = data["access_token"]
        ttl = max(data.get("expires_in", 3600) - _TOKEN_BUFFER_SECS, 0)
        cache.set(TOKEN_CACHE_KEY, token, timeout=ttl)
        logger.debug("PayPal token refreshed (expires_in=%s)", data.get("expires_in"))
        return token

    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Low-level HTTP with retry
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        prefer: str | None = None,
        paypal_request_id: str | None = None,
    ) -> dict:
        url = f"{self._base_url}{path}"
        headers = self._auth_headers()
        if prefer:
            headers["Prefer"] = prefer
        if paypal_request_id:
            headers["PayPal-Request-Id"] = paypal_request_id

        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = self._session.request(
                    method, url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=self._timeout,
                )
                return self._handle_response(resp)
            except PayPalRetryableError as exc:
                last_exc = exc
                wait = 2 ** (attempt - 1)
                logger.warning(
                    "PayPal retryable error (attempt %d/%d): %s – retrying in %ds",
                    attempt, self._max_retries, exc, wait,
                )
                time.sleep(wait)
            except PayPalAuthError:
                cache.delete(TOKEN_CACHE_KEY)
                headers = self._auth_headers()
                if attempt == self._max_retries:
                    raise

        raise last_exc  # type: ignore[misc]

    def _handle_response(self, resp: requests.Response) -> dict:
        if resp.status_code in (200, 201):
            return resp.json() if resp.content else {}
        if resp.status_code == 204:
            return {}
        if resp.status_code in (429, 503, 504):
            raise PayPalRetryableError(
                f"PayPal transient error {resp.status_code}",
                status_code=resp.status_code,
                details=self._safe_json(resp),
            )
        if resp.status_code == 401:
            cache.delete(TOKEN_CACHE_KEY)
            raise PayPalAuthError(
                "PayPal authentication failed",
                status_code=resp.status_code,
                details=self._safe_json(resp),
            )
        raise PayPalOrderError(
            f"PayPal API error {resp.status_code}",
            status_code=resp.status_code,
            details=self._safe_json(resp),
        )

    @staticmethod
    def _safe_json(resp: requests.Response) -> dict:
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text[:500]}
