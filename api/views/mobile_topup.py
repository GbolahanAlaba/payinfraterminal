import logging
import time
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from modules.utils.api.auth import authenticate_client
from modules.utils.api.misc import create_or_update_api_usage
from transactions.models import TransactionAttempt
from transactions.models import Transaction
from api.serializers import MobileTopupSerializer
from routing.engine import PaymentRouteEngine
from modules.core.response import success_response, error_response

log = logging.getLogger(__name__)


class MobileTopupAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        start_time = time.perf_counter()
        
        api_client = authenticate_client(request)
        serializer = MobileTopupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        topup_type = serializer.validated_data["topup_type"]
        network = serializer.validated_data["network"]
        phone_number = serializer.validated_data["phone_number"]
        amount = serializer.validated_data.get("amount")
        sender_name = serializer.validated_data.get("sender_name")
        reference = serializer.validated_data.get("reference")
        callback_url=serializer.validated_data.get("callback_url")

        if Transaction.objects.filter(reference=reference).exists():
            return error_response(
                status_code=400,
                message="reference must be unique",
                errors="reference already exist"
            )

        engine = PaymentRouteEngine(client=api_client)
        merchant = api_client.merchant

        try:
            credentials = engine.get_provider_credentials(provider)
            mobile_topup_response = engine.route_mobile_topup(
                provider=provider,
                topup_type=topup_type,
                network=network,
                phone_number=phone_number,
                amount=amount,
                reference=reference,
                sender_name=sender_name,
                credentials=credentials,
                callback_url=callback_url,
            )

            latency = (time.perf_counter() - start_time) * 1000

            create_or_update_api_usage(
                api_client,
                "airtime",
                "post",
                200,
                latency
            )

            cleaned = mobile_topup_response.get("cleaned_data", {})
            reference = cleaned.get("reference")
            
            transaction = Transaction.create_transaction(
                merchant=merchant,
                api_client=api_client,
                amount=amount,
                reference=reference,
                customer_phone=phone_number,
                currency="NGN",
                preferred_provider=provider,
                final_provider=provider,
                latency=latency,
                metadata={"payment_response": mobile_topup_response},
            )

            TransactionAttempt.create_transaction_attempt(
                transaction, 
                provider, 
                provider_reference=reference,
                response=mobile_topup_response)

            return success_response(
                mobile_topup_response,
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

            return error_response(
                status_code=400,
                message=str(e),
                errors=str(e),
            )

