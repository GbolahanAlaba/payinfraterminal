
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from merchants.models import Merchant
from merchants.serializers import MerchantUpdateSerializer
from modules.core.response import success_response



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