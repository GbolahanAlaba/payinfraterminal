
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiExample
from merchants.models import Merchant
from merchants.serializers import MerchantUpdateSerializer
from modules.core.response import success_response
from merchants.serializers import ToggleMerchantModeSerializer



class MerchantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update a merchant",
        description="Update fields of a merchant. Only the fields provided will be updated.",
        request=MerchantUpdateSerializer,
        responses={
            200: MerchantUpdateSerializer,
            404: OpenApiExample(
                "Not Found Example",
                value={"detail": "Merchant not found."},
                response_only=True
            ),
        },
        examples=[
            OpenApiExample(
                "Update Merchant Example",
                value={
                    "business_name": "New Business Name",
                    "business_email": "contact@newbusiness.com",
                    "business_phone": "+2348012345678",
                    "merchant_type": "llc",
                    "website": "https://newsite.com",
                    "address": "123 Business Street, Lagos",
                    "country": "Nigeria",
                    "state": "Lagos",
                    "registration_number": "RC1234567"
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        """
        PATCH endpoint to update a Merchant
        """
        try:
            merchant = Merchant.objects.get(pk=pk, user=request.user)
        except Merchant.DoesNotExist:
            return Response({"detail": "Merchant not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MerchantUpdateSerializer(merchant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, status_code=status.HTTP_200_OK)
    

class ToggleMerchantModeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Switch Merchant Live Mode",
        description="""
        Enable or disable live mode for the authenticated merchant.

        - `true` → Production transactions enabled
        - `false` → Sandbox mode only

        Merchant must be verified before enabling live mode.
        """,
        request=ToggleMerchantModeSerializer,
        responses={
            200: OpenApiResponse(
                description="Live mode updated successfully"
            ),
            403: OpenApiResponse(
                description="Merchant not verified"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
        },
        examples=[
            OpenApiExample(
                name="Enable Live Mode",
                value={"live_mode": True},
                request_only=True,
            ),
            OpenApiExample(
                name="Disable Live Mode",
                value={"live_mode": False},
                request_only=True,
            ),
        ],
    )
    @transaction.atomic
    def patch(self, request):
        merchant = get_object_or_404(Merchant, user=request.user)

        serializer = ToggleMerchantModeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merchant.live_mode = serializer.validated_data["live_mode"]
        merchant.save(update_fields=["live_mode"])

        return success_response(
            {
                "status": "success",
                "message": f"Live mode turned {'ON' if merchant.live_mode else 'OFF'}",
                "live_mode": merchant.live_mode,
            },
            status_code=status.HTTP_200_OK,
        )
