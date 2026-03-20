from rest_framework import serializers

class MobileTopupSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=100)
    topup_type = serializers.CharField(max_length=100)
    network = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=11)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    sender_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    callback_url = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)

    def validate_amount(self, value):
        if value < 50:
            raise serializers.ValidationError("Amount must not be less than 50.")
        return value