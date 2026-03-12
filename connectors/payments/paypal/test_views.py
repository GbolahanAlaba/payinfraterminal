"""Integration tests for PayPal DRF views."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

WEBHOOK_HEADERS = {
    "HTTP_PAYPAL_TRANSMISSION_ID": "tid123",
    "HTTP_PAYPAL_TRANSMISSION_TIME": "2024-01-01T00:00:00Z",
    "HTTP_PAYPAL_CERT_URL": "https://api.sandbox.paypal.com/v1/notifications/certs/cert",
    "HTTP_PAYPAL_AUTH_ALGO": "SHA256withRSA",
    "HTTP_PAYPAL_TRANSMISSION_SIG": "sig123",
}


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username="testuser", password="pass")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestCreateOrderView:
    @patch("paypal.views.paypal_client")
    def test_success(self, mock_client, auth_client):
        mock_client.create_order.return_value = {
            "id": "PP1",
            "status": "CREATED",
            "links": [{"rel": "approve", "href": "https://sandbox.paypal.com/approve"}],
        }
        resp = auth_client.post(
            "/api/payments/paypal/orders/",
            {"total_amount": "49.99", "currency_code": "USD"},
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["paypal_order_id"] == "PP1"
        assert resp.data["approval_url"] == "https://sandbox.paypal.com/approve"

    def test_unauthenticated(self, api_client):
        resp = api_client.post("/api/payments/paypal/orders/", {"total_amount": "10.00"}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_missing_total_amount(self, auth_client):
        resp = auth_client.post("/api/payments/paypal/orders/", {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch("paypal.views.paypal_client")
    def test_paypal_error_returns_502(self, mock_client, auth_client):
        from paypal.exceptions import PayPalOrderError
        mock_client.create_order.side_effect = PayPalOrderError("Bad", 422, {})
        resp = auth_client.post(
            "/api/payments/paypal/orders/",
            {"total_amount": "10.00"},
            format="json",
        )
        assert resp.status_code == status.HTTP_502_BAD_GATEWAY


@pytest.mark.django_db
class TestCaptureOrderView:
    @patch("paypal.views.paypal_client")
    def test_success(self, mock_client, auth_client):
        mock_client.capture_order.return_value = {
            "id": "PP1",
            "status": "COMPLETED",
            "purchase_units": [{"payments": {"captures": [{"id": "CAP1"}]}}],
        }
        resp = auth_client.post("/api/payments/paypal/orders/PP1/capture/", format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["capture_id"] == "CAP1"
        assert resp.data["status"] == "COMPLETED"


@pytest.mark.django_db
class TestRefundView:
    @patch("paypal.views.paypal_client")
    def test_full_refund(self, mock_client, auth_client):
        mock_client.refund_capture.return_value = {"id": "REF1", "status": "COMPLETED"}
        resp = auth_client.post(
            "/api/payments/paypal/refunds/",
            {"capture_id": "CAP1"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["refund_id"] == "REF1"

    @patch("paypal.views.paypal_client")
    def test_partial_refund(self, mock_client, auth_client):
        mock_client.refund_capture.return_value = {"id": "REF2", "status": "COMPLETED"}
        resp = auth_client.post(
            "/api/payments/paypal/refunds/",
            {"capture_id": "CAP1", "amount": {"currency_code": "USD", "value": "5.00"}},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestWebhookView:
    @patch("paypal.views.dispatch")
    @patch("paypal.views.paypal_client")
    def test_valid_webhook_dispatches(self, mock_client, mock_dispatch, api_client):
        mock_client.verify_signature.return_value = True
        payload = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "id": "EVT1",
            "resource": {"id": "CAP1", "custom_id": "ORD-123"},
        }
        resp = api_client.post(
            "/api/payments/paypal/webhook/",
            data=json.dumps(payload),
            content_type="application/json",
            **WEBHOOK_HEADERS,
        )
        assert resp.status_code == status.HTTP_200_OK
        mock_dispatch.assert_called_once_with(
            event_type="PAYMENT.CAPTURE.COMPLETED",
            resource={"id": "CAP1", "custom_id": "ORD-123"},
            raw_event=payload,
        )

    @patch("paypal.views.paypal_client")
    def test_invalid_signature_rejected(self, mock_client, api_client):
        mock_client.verify_signature.return_value = False
        resp = api_client.post(
            "/api/payments/paypal/webhook/",
            data=json.dumps({"event_type": "PAYMENT.CAPTURE.COMPLETED"}),
            content_type="application/json",
            **WEBHOOK_HEADERS,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch("paypal.views.dispatch")
    @patch("paypal.views.paypal_client")
    def test_handler_exception_still_returns_200(self, mock_client, mock_dispatch, api_client):
        """PayPal must never receive a 5xx — handler errors are swallowed."""
        mock_client.verify_signature.return_value = True
        mock_dispatch.side_effect = RuntimeError("DB down")
        resp = api_client.post(
            "/api/payments/paypal/webhook/",
            data=json.dumps({"event_type": "PAYMENT.CAPTURE.COMPLETED", "resource": {}}),
            content_type="application/json",
            **WEBHOOK_HEADERS,
        )
        assert resp.status_code == status.HTTP_200_OK
