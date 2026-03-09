from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from modules.core.response import success_response

from api.models import APIClient
from api.serializers import RegenerateAPIKeysSerializer, UpdateWebhookURLSerializer

class RegenerateAPIKeysView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Regenerate API Keys",
        description=(
            "Regenerates the public and secret API keys for a merchant's API client.\n\n"
            "The `raw_secret` is returned only once and must be stored securely."
        ),
        responses={
            200: OpenApiResponse(
                response=RegenerateAPIKeysSerializer,
                description="API keys regenerated successfully"
            ),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="API client not found"),
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "status": "success",
                    "message": "API keys regenerated successfully",
                    "data": {
                        "client_public_key": "pit_pk_live_3a4f2b1c9d8e7f0a",
                        "client_secret_key": "pit_sk_live_Af9kL2s1W0d9vTz8QjR7hP0x",
                        "environment": "LIVE"
                    },
                    "meta": {
                        "request_id": "d8e9f3a1-4a63-4c8b-9f33-2e8a6b9e1c2d",
                        "timestamp": "2026-03-06T14:15:22Z"
                    },
                    "raw_secret": "pit_sk_live_Af9kL2s1W0d9vTz8QjR7hP0x"
                },
                response_only=True
            )
        ],
        tags=["API"]
    )
    def post(self, request, client_id):
        """
        Regenerate API keys for a merchant's client.
        """

        try:
            api_client = APIClient.objects.get(
                id=client_id,
                merchant__user=request.user
            )
        except APIClient.DoesNotExist:
            return Response({
                "status": "error",
                "message": "API client not found."
            }, status=status.HTTP_404_NOT_FOUND)

        raw_secret = api_client.generate_credentials()

        serializer = RegenerateAPIKeysSerializer(api_client)

        response_data = serializer.data
        response_data["raw_secret"] = raw_secret

        return success_response(
            data=response_data,
            message="API keys regenerated successfully",
            status_code=status.HTTP_200_OK
        )


class UpdateWebhookURLView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update Webhook URL",
        description="Updates the webhook URL for a merchant's API client.",
        request=OpenApiResponse(
            response=RegenerateAPIKeysSerializer,
            description="Webhook URL updated successfully"
        ),
         responses={
            200: OpenApiResponse(description="Webhook URL updated successfully"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="API client not found"),
        },
        tags=["API"]
    )
    def patch(self, request, client_id):
        """
        Update the webhook URL for a merchant's API client.
        """

        try:
            api_client = APIClient.objects.get(
                id=client_id,
                merchant__user=request.user
            )
        except APIClient.DoesNotExist:
            return Response({
                "status": "error",
                "message": "API client not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateWebhookURLSerializer(api_client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Webhook URL updated successfully",
            status_code=status.HTTP_200_OK
        )