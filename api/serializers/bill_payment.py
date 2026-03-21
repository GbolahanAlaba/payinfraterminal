from rest_framework import serializers

class BillPaymentSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=100)
    disco = serializers.CharField(max_length=100)
    meter_type = serializers.CharField(max_length=100)
    customer_id = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payer_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=11)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    callback_url = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)

    def validate_amount(self, value):
        if value < 1000:
            raise serializers.ValidationError("Amount must not be less than 1000.")
        return value