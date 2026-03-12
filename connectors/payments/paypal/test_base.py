"""Tests for PayPalBase – auth, retry, response handling."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

PAYPAL_SETTINGS = {
    "CLIENT_ID": "test_client_id",
    "CLIENT_SECRET": "test_secret",
    "ENVIRONMENT": "sandbox",
    "WEBHOOK_ID": "WH-TEST123",
}


@pytest.mark.django_db
class TestAuth:
    @patch("paypal.base.requests.Session.post")
    def test_token_fetched_and_cached(self, mock_post, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.base import PayPalBase
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "TOK", "expires_in": 3600}
        client = PayPalBase()
        assert client._get_access_token() == "TOK"
        # Second call should use cache, not hit the network again
        assert client._get_access_token() == "TOK"
        mock_post.assert_called_once()

    @patch("paypal.base.requests.Session.post")
    def test_bad_credentials_raises_auth_error(self, mock_post, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.base import PayPalBase
        from paypal.exceptions import PayPalAuthError
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"error": "invalid_client"}
        mock_post.return_value.content = b'{"error":"invalid_client"}'
        with pytest.raises(PayPalAuthError):
            PayPalBase()._get_access_token()


@pytest.mark.django_db
class TestResponseHandling:
    def _client(self, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.base import PayPalBase
        c = PayPalBase.__new__(PayPalBase)
        c._base_url = "https://api-m.sandbox.paypal.com"
        return c

    def test_204_returns_empty_dict(self, settings):
        from paypal.base import PayPalBase
        client = self._client(settings)
        resp = MagicMock(status_code=204, content=b"")
        assert client._handle_response(resp) == {}

    def test_429_raises_retryable(self, settings):
        from paypal.base import PayPalBase
        from paypal.exceptions import PayPalRetryableError
        client = self._client(settings)
        resp = MagicMock(status_code=429, content=b"{}")
        resp.json.return_value = {}
        with pytest.raises(PayPalRetryableError):
            client._handle_response(resp)

    def test_422_raises_order_error(self, settings):
        from paypal.base import PayPalBase
        from paypal.exceptions import PayPalOrderError
        client = self._client(settings)
        resp = MagicMock(status_code=422, content=b"{}")
        resp.json.return_value = {"name": "UNPROCESSABLE_ENTITY"}
        with pytest.raises(PayPalOrderError):
            client._handle_response(resp)
