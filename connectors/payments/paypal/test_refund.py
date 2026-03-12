"""Tests for PayPalRefund."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

PAYPAL_SETTINGS = {
    "CLIENT_ID": "test_client_id",
    "CLIENT_SECRET": "test_secret",
    "ENVIRONMENT": "sandbox",
    "WEBHOOK_ID": "WH-TEST",
}


@pytest.mark.django_db
class TestRefund:
    @patch("paypal.base.PayPalBase._request")
    def test_full_refund(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.refund import PayPalRefund
        mock_req.return_value = {"id": "REFUND1", "status": "COMPLETED"}
        result = PayPalRefund().refund_capture("CAP1")
        assert result["id"] == "REFUND1"
        # No amount in payload for full refund
        _, kwargs = mock_req.call_args
        assert "amount" not in kwargs.get("json", {})

    @patch("paypal.base.PayPalBase._request")
    def test_partial_refund(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.base import Money
        from paypal.refund import PayPalRefund
        mock_req.return_value = {"id": "REFUND2", "status": "COMPLETED"}
        result = PayPalRefund().refund_capture("CAP1", amount=Money("USD", Decimal("5.00")))
        assert result["id"] == "REFUND2"
        _, kwargs = mock_req.call_args
        assert kwargs["json"]["amount"] == {"currency_code": "USD", "value": "5.00"}

    @patch("paypal.base.PayPalBase._request")
    def test_get_refund(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.refund import PayPalRefund
        mock_req.return_value = {"id": "REFUND1", "status": "COMPLETED"}
        result = PayPalRefund().get_refund("REFUND1")
        assert result["id"] == "REFUND1"
