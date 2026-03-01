from rest_framework import serializers

class PaymentRequestSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reference = serializers.CharField(max_length=100, required=False)
    secret_key = serializers.CharField(max_length=100)
    callback_url = serializers.CharField(max_length=100, required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value