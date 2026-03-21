from rest_framework import serializers
from transactions.models import Transaction


class TransactionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = [
            "transaction_id",
            "transaction_type",
            "transaction_source",
            "preferred_provider",
            "amount",
            "currency",
            "channel",
            "reference",
            "customer_email",
            "customer_phone",
            "metadata",
        ]


class TransactionResponseSerializer(serializers.ModelSerializer):
    preferred_provider = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_preferred_provider(self, obj):
        return obj.provider

    def get_channel(self, obj):
        return getattr(obj.collection, "channel", None)

    def get_customer_email(self, obj):
        return getattr(obj.collection, "customer_email", None)

    def get_metadata(self, obj):
        return getattr(obj.collection, "metadata", None)