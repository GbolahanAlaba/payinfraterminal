# modules/payments/nomba/base.py

import requests
import time
import logging
from datetime import datetime
from modules.utils.utils import ServiceProvidersEnvironment

log = logging.getLogger("my_logger")


class NombaBase:
    def __init__(self):
        self.environment = ServiceProvidersEnvironment.get_nomba_environment_details()
        self.base_url = self.environment["URL"]

        self.tokens = {
            "access_token": None,
            "refresh_token": None,
            "expiry_time": 0,
        }

        self.timeout = 30

    # =====================
    # Token Management
    # =====================
    def _update_tokens(self, token_data: dict):
        self.tokens["access_token"] = token_data.get("access_token")
        self.tokens["refresh_token"] = token_data.get(
            "refresh_token", self.tokens["refresh_token"]
        )

        expires_at = token_data.get("expiresAt")
        if expires_at:
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            self.tokens["expiry_time"] = expires_at.timestamp()
        else:
            self.tokens["expiry_time"] = time.time() + 3600

    def _get_new_access_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.environment["NOMBA_CLIENT_ID"],
            "client_secret": self.environment["NOMBA_CLIENT_SECRET"],
        }

        headers = {
            "Content-Type": "application/json",
            "accountId": self.environment["NOMBA_ACCOUNT_ID"],
        }

        response = requests.post(
            f"{self.base_url}/auth/token/issue",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        if data.get("code") != "00":
            raise Exception(data.get("message", "Failed to issue token"))

        self._update_tokens(data["data"])

    def _refresh_access_token(self):
        payload = {
            "grant_type": "client_credentials",
            "refresh_token": self.tokens["refresh_token"],
        }

        headers = self._headers(include_auth=True)

        response = requests.post(
            f"{self.base_url}/auth/token/issue",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()
        self._update_tokens(response.json()["data"])

    def _ensure_token(self):
        if not self.tokens["access_token"] or time.time() >= self.tokens["expiry_time"]:
            try:
                self._refresh_access_token()
            except Exception:
                self._get_new_access_token()

    def _headers(self, include_auth=False):
        headers = {
            "Content-Type": "application/json",
            "accountId": self.environment["NOMBA_ACCOUNT_ID"],
        }
        if include_auth:
            headers["Authorization"] = f"Bearer {self.tokens['access_token']}"
        return headers

    # =====================
    # HTTP Helpers (Paystack-like)
    # =====================
    def _request(self, method, endpoint, params=None, json=None):
        self._ensure_token()

        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self._headers(include_auth=True),
            params=params,
            json=json,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            log.error("Nomba error: %s", response.text)
            raise

        return response.json()

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, json=None):
        return self._request("POST", endpoint, json=json)
