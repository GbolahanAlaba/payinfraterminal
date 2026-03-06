from rest_framework import serializers
from api.models import ClientProviderCredential, ClientProvider, APIClient, Environment, PaymentProvider


class ClientProviderCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProviderCredential
        fields = [
            "id",
            "credentials",
            "credential_type",
            "is_encrypted",
            "created_at",
            "updated_at",
        ]

class ClientProviderSerializer(serializers.ModelSerializer):
    credentials = ClientProviderCredentialSerializer(read_only=True)

    class Meta:
        model = ClientProvider
        fields = [
            "id",
            "provider",
            "is_active",
            "created_at",
            "credentials",
        ]

class APIClientSerializer(serializers.ModelSerializer):
    providers = ClientProviderSerializer(many=True, read_only=True)

    class Meta:
        model = APIClient
        fields = [
            "id",
            "client_name",
            "client_public_key",
            "client_secret_key",  # Avoid exposing raw secret
            "environment",
            "status",
            "providers",
        ]

class RegenerateAPIKeysSerializer(serializers.ModelSerializer):
    environment = serializers.ReadOnlyField()

    class Meta:
        model = APIClient
        fields = ["client_public_key", "client_secret_key", "environment"]


class SetupClientProviderSerializer(serializers.Serializer):
    merchant_id = serializers.CharField()
    environment = serializers.ChoiceField(choices=Environment.choices)
    provider = serializers.ChoiceField(choices=PaymentProvider.choices)
    credentials = serializers.JSONField()
    credential_type = serializers.CharField(default="api_key")