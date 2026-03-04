from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample
)
from django.shortcuts import get_object_or_404
from django.db import transaction
from api.models import APIClient, ClientProvider, ClientProviderCredential
from api.serializers import SetupClientProviderSerializer
from merchants.models import Merchant


class SetupClientProviderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Client Provider"],
        summary="Setup or Update Client Provider Credentials",
        description="""
        Configure a payment provider (e.g Paystack, Flutterwave) 
        for a specific merchant and environment (Live or Sandbox).

        If provider already exists → credentials will be updated.
        If provider does not exist → it will be created.
        """,
        request=SetupClientProviderSerializer,
        responses={
            200: OpenApiResponse(
                description="Provider configured successfully"
            ),
            400: OpenApiResponse(
                description="Validation error"
            ),
            404: OpenApiResponse(
                description="Merchant or API client not found"
            ),
        },
        examples=[
            OpenApiExample(
                name="Sandbox Setup Example",
                value={
                    "merchant_id": "165714267",
                    "environment": "Sandbox",
                    "provider": "paystack",
                    "credential_type": "api_key",
                    "credentials": {
                        "public_key": "pk_test_xxxxx",
                        "secret_key": "sk_test_xxxxx"
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Live Setup Example",
                value={
                    "merchant_id": "165714267",
                    "environment": "live",
                    "provider": "paystack",
                    "credential_type": "api_key",
                    "credentials": {
                        "public_key": "pk_live_xxxxx",
                        "secret_key": "sk_live_xxxxx"
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Success Response",
                value={
                    "status": "success",
                    "message": "paystack configured successfully for live"
                },
                response_only=True,
                status_codes=["200"]
            ),
        ],
    )
    @transaction.atomic
    def post(self, request):
        serializer = SetupClientProviderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merchant_id = serializer.validated_data["merchant_id"]
        environment = serializer.validated_data["environment"]
        provider_name = serializer.validated_data["provider"]
        credentials_data = serializer.validated_data["credentials"]
        credential_type = serializer.validated_data["credential_type"]

        merchant = get_object_or_404(
            Merchant,
            merchant_id=merchant_id,
            user=request.user
        )

        api_client = get_object_or_404(
            APIClient,
            merchant=merchant,
            environment=environment
        )

        client_provider, created = ClientProvider.objects.get_or_create(
            client=api_client,
            provider=provider_name.lower(),
            defaults={"is_active": True}
        )

        if not created:
            client_provider.is_active = True
            client_provider.save()

        ClientProviderCredential.objects.update_or_create(
            client_provider=client_provider,
            defaults={
                "credentials": credentials_data,
                "credential_type": credential_type,
                "is_encrypted": False  # change if you encrypt
            }
        )

        return Response({
            "status": "success",
            "message": f"{provider_name.lower()} configured successfully for {environment}"
        }, status=status.HTTP_200_OK)