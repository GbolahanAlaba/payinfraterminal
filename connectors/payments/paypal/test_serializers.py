"""Tests for PayPal DRF serializers."""
from decimal import Decimal

import pytest
from paypal.serializers import CreateOrderSerializer, RefundSerializer


class TestCreateOrderSerializer:
    def test_minimal_valid(self):
        s = CreateOrderSerializer(data={"total_amount": "10.00"})
        assert s.is_valid(), s.errors

    def test_default_intent_is_capture(self):
        s = CreateOrderSerializer(data={"total_amount": "10.00"})
        s.is_valid()
        assert s.validated_data["intent"] == "CAPTURE"

    def test_item_total_mismatch_fails(self):
        s = CreateOrderSerializer(data={
            "total_amount": "99.00",
            "currency_code": "USD",
            "items": [{"name": "Widget", "unit_amount": {"currency_code": "USD", "value": "10.00"}, "quantity": 2}],
        })
        assert not s.is_valid()

    def test_item_total_match_passes(self):
        s = CreateOrderSerializer(data={
            "total_amount": "20.00",
            "currency_code": "USD",
            "items": [{"name": "Widget", "unit_amount": {"currency_code": "USD", "value": "10.00"}, "quantity": 2}],
        })
        assert s.is_valid(), s.errors

    def test_negative_total_fails(self):
        s = CreateOrderSerializer(data={"total_amount": "-5.00"})
        assert not s.is_valid()

    def test_invalid_intent_fails(self):
        s = CreateOrderSerializer(data={"total_amount": "10.00", "intent": "INVALID"})
        assert not s.is_valid()


class TestRefundSerializer:
    def test_capture_id_required(self):
        s = RefundSerializer(data={})
        assert not s.is_valid()
        assert "capture_id" in s.errors

    def test_valid_full_refund(self):
        s = RefundSerializer(data={"capture_id": "CAP123"})
        assert s.is_valid(), s.errors

    def test_valid_partial_refund(self):
        s = RefundSerializer(data={
            "capture_id": "CAP123",
            "amount": {"currency_code": "USD", "value": "5.00"},
        })
        assert s.is_valid(), s.errors
