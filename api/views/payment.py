from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import PaymentRequestSerializer
from modules.utils.api.auth import authenticate_client
from api.models import APIUsageRecord


class ProcessPaymentAPIView(APIView):
    authentication_classes = []  # we handle manually
    permission_classes = []

    def post(self, request):
        api_client = authenticate_client(request)

        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        amount = serializer.validated_data["amount"]

        APIUsageRecord.objects.create(
            client=api_client,
            endpoint="process_payment",
            request_count=1
        )

        response_data = {
            "status": "success",
            "merchant": api_client.merchant.business_name,
            "provider": provider,
            "amount": amount,
            "environment": api_client.environment
        }

        return Response(response_data, status=status.HTTP_200_OK)