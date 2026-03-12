"""
DRF serializers for PayPal API views.
"""
from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class MoneySerializer(serializers.Serializer):
    currency_code = serializers.CharField(max_length=3)
    value = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )


class OrderItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=127)
    unit_amount = MoneySerializer()
    quantity = serializers.IntegerField(min_value=1, default=1)
    description = serializers.CharField(max_length=127, required=False, default="")
    sku = serializers.CharField(max_length=127, required=False, default="")
    category = serializers.ChoiceField(
        choices=["PHYSICAL_GOODS", "DIGITAL_GOODS", "DONATION"],
        default="PHYSICAL_GOODS",
    )


class CreateOrderSerializer(serializers.Serializer):
    intent = serializers.ChoiceField(choices=["CAPTURE", "AUTHORIZE"], default="CAPTURE")
    currency_code = serializers.CharField(max_length=3, default="USD")
    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    items = OrderItemSerializer(many=True, required=False, default=list)
    custom_id = serializers.CharField(max_length=127, required=False, default="")
    invoice_id = serializers.CharField(max_length=127, required=False, default="")
    description = serializers.CharField(max_length=127, required=False, default="")
    return_url = serializers.URLField(required=False, default="")
    cancel_url = serializers.URLField(required=False, default="")
    shipping_preference = serializers.ChoiceField(
        choices=["NO_SHIPPING", "GET_FROM_FILE", "SET_PROVIDED_ADDRESS"],
        default="NO_SHIPPING",
    )

    def validate(self, attrs: dict) -> dict:
        items = attrs.get("items", [])
        if items:
            computed = sum(
                Decimal(str(i["unit_amount"]["value"])) * i["quantity"]
                for i in items
            )
            if computed != attrs["total_amount"]:
                raise serializers.ValidationError(
                    f"total_amount ({attrs['total_amount']}) does not match "
                    f"sum of item totals ({computed})."
                )
        return attrs


class RefundSerializer(serializers.Serializer):
    capture_id = serializers.CharField(max_length=64)
    amount = MoneySerializer(required=False)
    note_to_payer = serializers.CharField(max_length=255, required=False, default="")
    invoice_id = serializers.CharField(max_length=127, required=False, default="")
