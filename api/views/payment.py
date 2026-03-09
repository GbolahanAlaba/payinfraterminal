import logging
import time
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import PaymentRequestSerializer
from modules.utils.api.auth import authenticate_client
from modules.utils.api.misc import create_or_update_api_usage
from transactions.models import TransactionAttempt
from transactions.models import Transaction
from routing.engine import PaymentRouteEngine
from modules.core.response import success_response

log = logging.getLogger(__name__)


class ProcessPaymentAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Process a payment",
        description="Processes a payment through the PaymentRouteEngine. Merchants must provide their public and secret keys in headers.",
        parameters=[
            OpenApiParameter(
                name="Client-Public-Key",
                location=OpenApiParameter.HEADER,
                description="Your merchant public key",
                required=True,
                type=str
            ),
            OpenApiParameter(
                name="Client-Secret-Key",
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
                                "payment_url": "https://checkout-v2.dev-flutterwave.com/v3/hosted/pay/72fec2269cd27725212a",
                                "access_code": "FAADE880352C",
                                "reference": "FAADE880352C",
                                "amount": "10000.00",
                                "currency": "NGN",
                                "metadata": {},
                                "provider": "flutterwave",
                                "link": "https://checkout-v2.dev-flutterwave.com/v3/hosted/pay/72fec2269cd27725212a",
                                "tx_ref": "FAADE880352C",
                                "redirect_url": "https://payflow.com/payments/",
                                "status": "success"
                            }
                        }
                    }
                }
            },
            400: {"description": "Invalid request"},
            401: {"description": "Unauthorized"},
        },
        tags=["API"]
    )
    def post(self, request):
        start_time = time.perf_counter()
        
        api_client = authenticate_client(request)
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        currency = serializer.validated_data.get("currency") or "NGN"
        reference = serializer.validated_data.get("reference")
        callback_url = serializer.validated_data.get("callback_url")

        engine = PaymentRouteEngine(client=api_client)
        merchant = api_client.merchant

        try:
            credentials = engine.get_provider_credentials(provider)
            payment_response = engine.route_payment(
                provider=provider,
                amount=amount,
                currency=currency,
                email=email,
                reference=reference,
                secret_key=credentials,
                callback_url=callback_url,
            )

            latency = (time.perf_counter() - start_time) * 1000

            create_or_update_api_usage(
                api_client,
                "initiate-payment",
                "post",
                200,
                latency
            )

            transaction = Transaction.create_transaction(
                merchant=merchant,
                amount=amount,
                reference=payment_response.get("reference"),
                customer_email=email,
                currency=currency,
                preferred_provider=provider,
                final_provider=provider,
                latency=latency,
                metadata={"payment_response": payment_response},
            )

            TransactionAttempt.create_transaction_attempt(
                transaction, 
                provider, 
                provider_reference=payment_response.get("reference"), 
                response=payment_response)

            return success_response(
                payment_response,
                message="Payment initiated successfully",
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            create_or_update_api_usage(
                api_client,
                "initiate-payment",
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