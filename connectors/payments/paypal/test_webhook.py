"""Tests for PayPalWebhook – signature verification and event dispatch."""
from __future__ import annotations

from unittest.mock import patch

import pytest

PAYPAL_SETTINGS = {
    "CLIENT_ID": "test_client_id",
    "CLIENT_SECRET": "test_secret",
    "ENVIRONMENT": "sandbox",
    "WEBHOOK_ID": "WH-TEST",
}


@pytest.mark.django_db
class TestWebhookVerification:
    @patch("paypal.base.PayPalBase._request")
    def test_valid_signature(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.webhook import PayPalWebhook
        mock_req.return_value = {"verification_status": "SUCCESS"}
        wh = PayPalWebhook()
        assert wh.verify_signature(
            transmission_id="tid",
            timestamp="2024-01-01T00:00:00Z",
            cert_url="https://api.sandbox.paypal.com/v1/notifications/certs/cert",
            auth_algo="SHA256withRSA",
            actual_sig="sig",
            body=b'{"event_type":"PAYMENT.CAPTURE.COMPLETED"}',
        ) is True

    @patch("paypal.base.PayPalBase._request")
    def test_invalid_signature(self, mock_req, settings):
        settings.PAYPAL = PAYPAL_SETTINGS
        from paypal.webhook import PayPalWebhook
        mock_req.return_value = {"verification_status": "FAILURE"}
        wh = PayPalWebhook()
        assert wh.verify_signature(
            transmission_id="tid",
            timestamp="2024-01-01T00:00:00Z",
            cert_url="https://example.com/cert",
            auth_algo="SHA256withRSA",
            actual_sig="badsig",
            body=b"{}",
        ) is False

    def test_missing_webhook_id_raises(self, settings):
        settings.PAYPAL = {**PAYPAL_SETTINGS, "WEBHOOK_ID": ""}
        from paypal.exceptions import PayPalWebhookError
        from paypal.webhook import PayPalWebhook
        with pytest.raises(PayPalWebhookError):
            PayPalWebhook().verify_signature(
                transmission_id="", timestamp="", cert_url="",
                auth_algo="", actual_sig="", body=b"",
            )


class TestDispatcher:
    def test_registered_handler_called(self):
        from paypal.webhook import _HANDLERS, dispatch, register

        received = []

        @register("TEST.DISPATCH.EVENT")
        def handler(resource, raw_event):
            received.append(resource)

        dispatch(event_type="TEST.DISPATCH.EVENT", resource={"id": "X"}, raw_event={})
        assert {"id": "X"} in received

        # clean up
        _HANDLERS.pop("TEST.DISPATCH.EVENT", None)

    def test_unknown_event_no_error(self):
        from paypal.webhook import dispatch
        dispatch(event_type="NO.HANDLER.FOR.THIS", resource={}, raw_event={})

    def test_multiple_handlers_all_called(self):
        from paypal.webhook import _HANDLERS, dispatch, register

        log = []

        @register("MULTI.TEST.EVENT")
        def h1(resource, raw_event):
            log.append("h1")

        @register("MULTI.TEST.EVENT")
        def h2(resource, raw_event):
            log.append("h2")

        dispatch(event_type="MULTI.TEST.EVENT", resource={}, raw_event={})
        assert log == ["h1", "h2"]

        _HANDLERS.pop("MULTI.TEST.EVENT", None)
