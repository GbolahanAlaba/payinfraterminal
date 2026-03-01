from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import PaymentRequestSerializer
from modules.utils.api.auth import authenticate_client
from modules.utils.api.misc import create_or_update_api_usage
from routing.engine import PaymentRouteEngine


class ProcessPaymentAPIView(APIView):
    authentication_classes = []  # handled manually
    permission_classes = []

    def post(self, request):
        api_client = authenticate_client(request)

        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        reference = serializer.validated_data.get("reference")
        secret_key = serializer.validated_data["secret_key"]
        callback_url = serializer.validated_data.get("callback_url")

        engine = PaymentRouteEngine()

        try:
            payment_response = engine.route_payment(
                provider=provider,
                amount=amount,
                email=email,
                reference=reference,
                secret_key=secret_key,
                callback_url=callback_url, 
            )

            create_or_update_api_usage(
                api_client,
                "process-payment",
                "post",
                200,
                "2"
            )

            return Response(payment_response, status=status.HTTP_200_OK)

        except Exception as e:
            create_or_update_api_usage(
                api_client,
                "process-payment",
                "post",
                400,
                "2"
            )

            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )