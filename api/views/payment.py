import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import PaymentRequestSerializer
from modules.utils.api.auth import authenticate_client
from modules.utils.api.misc import create_or_update_api_usage
from routing.engine import PaymentRouteEngine

log = logging.getLogger(__name__)


class ProcessPaymentAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Process a payment",
        description="Processes a payment through the PaymentRouteEngine. Merchants must provide their public and secret keys in headers.",
        parameters=[
            OpenApiParameter(
                name="X-Client-Public-Key",
                location=OpenApiParameter.HEADER,
                description="Your merchant public key",
                required=True,
                type=str
            ),
            OpenApiParameter(
                name="X-Client-Secret-Key",
                location=OpenApiParameter.HEADER,
                description="Your merchant secret key",
                required=True,
                type=str
            ),
        ],
        request=PaymentRequestSerializer,
        responses={
            200: {
                "description": "Payment processed successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "success",
                            "message": "Payment processed",
                            "data": {
                                "provider": "paystack",
                                "amount": 1000,
                                "reference": "abc123",
                                "status": "completed"
                            }
                        }
                    }
                }
            },
            400: {"description": "Invalid request"},
            401: {"description": "Unauthorized"},
        },
        tags=["Payments"]
    )
    def post(self, request):
        api_client = authenticate_client(request)
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        reference = serializer.validated_data.get("reference")
        callback_url = serializer.validated_data.get("callback_url")

        engine = PaymentRouteEngine(client=api_client)

        try:
            credentials = engine.get_provider_credentials(provider)
            payment_response = engine.route_payment(
                provider=provider,
                amount=amount,
                email=email,
                reference=reference,
                secret_key=credentials,
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


# class ProcessPaymentAPIView(APIView):
#     authentication_classes = []  # handled manually
#     permission_classes = []

#     def post(self, request):
#         api_client = authenticate_client(request)

#         serializer = PaymentRequestSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         provider = serializer.validated_data["provider"]
#         email = serializer.validated_data["email"]
#         amount = serializer.validated_data["amount"]
#         reference = serializer.validated_data.get("reference")
#         secret_key = serializer.validated_data["secret_key"]
#         callback_url = serializer.validated_data.get("callback_url")

#         engine = PaymentRouteEngine()

#         try:
#             payment_response = engine.route_payment(
#                 provider=provider,
#                 amount=amount,
#                 email=email,
#                 reference=reference,
#                 secret_key=secret_key,
#                 callback_url=callback_url, 
#             )

#             create_or_update_api_usage(
#                 api_client,
#                 "process-payment",
#                 "post",
#                 200,
#                 "2"
#             )

#             return Response(payment_response, status=status.HTTP_200_OK)

#         except Exception as e:
#             create_or_update_api_usage(
#                 api_client,
#                 "process-payment",
#                 "post",
#                 400,
#                 "2"
#             )

#             return Response(
#                 {
#                     "status": "error",
#                     "message": str(e),
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )