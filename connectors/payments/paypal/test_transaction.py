"""Tests for PayPalTransaction – create, capture, authorize."""
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
class TestTransaction:
    @patch("paypal.base.PayPalBase._request")
    def test_create_order(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.base import OrderRequest
        from paypal.transaction import PayPalTransaction
        mock_req.return_value = {"id": "ORDER1", "status": "CREATED", "links": []}
        client = PayPalTransaction()
        result = client.create_order(OrderRequest(intent="CAPTURE", currency_code="USD", total_amount=Decimal("20.00")))
        assert result["id"] == "ORDER1"

    @patch("paypal.base.PayPalBase._request")
    def test_capture_order(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.transaction import PayPalTransaction
        mock_req.return_value = {
            "id": "ORDER1",
            "status": "COMPLETED",
            "purchase_units": [{"payments": {"captures": [{"id": "CAP1"}]}}],
        }
        result = PayPalTransaction().capture_order("ORDER1")
        assert result["status"] == "COMPLETED"

    @patch("paypal.base.PayPalBase._request")
    def test_authorize_order(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.transaction import PayPalTransaction
        mock_req.return_value = {"id": "ORDER1", "status": "APPROVED"}
        result = PayPalTransaction().authorize_order("ORDER1")
        assert result["id"] == "ORDER1"

    @patch("paypal.base.PayPalBase._request")
    def test_void_authorization(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.transaction import PayPalTransaction
        mock_req.return_value = {}
        result = PayPalTransaction().void_authorization("AUTH1")
        assert result == {}
