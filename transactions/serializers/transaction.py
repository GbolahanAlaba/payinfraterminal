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

    class Meta:
        model = Transaction
        fields = "__all__"