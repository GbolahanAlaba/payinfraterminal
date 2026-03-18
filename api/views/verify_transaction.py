import logging
import time
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction as db_transaction
from transactions.models import Transaction, STATUS
from routing.engine import PaymentRouteEngine
from modules.utils.api.auth import authenticate_client
from modules.core.response import success_response, error_response
from connectors.payments.services.payment_services import PaymentService

log = logging.getLogger(__name__)


class VerifyTransactionView(APIView):
    permission_classes = []
    

    def __paystack__(self, reference, credentials):

        service = PaymentService(
            provider_name="paystack",
            secret_key=credentials["secret_key"]
        )

        response = service.verify_payment(reference=reference)

        metadata = response.get("data", {})
        status = metadata.get("status")
        authorization = metadata.get("authorization")
        channel = authorization.get("channel")
        message = response.get("message", "")

        if status in [True, "success", "successful"]:
            provider_status = "success"
        elif status in [False, "failed"]:
            provider_status = "failed"
        else:
            provider_status = "processing"

        return {
            "provider_status": provider_status,
            "channel": channel,
            "metadata": metadata,
            "message": message,
            "response": response
        }


    def __flutterwave__(self, reference, credentials):

        service = PaymentService(
            provider_name="flutterwave",
            secret_key=credentials["secret_key"]
        )

        response = service.verify_payment(reference=reference)

        metadata = response.get("data", {})
        status = metadata.get("status", "")
        channel = metadata.get("payment_type", "")
        message = metadata.get("processor_response", "")
        
        if status in [True, "success", "successful"]:
            provider_status = "success"
        elif status in [False, "failed"]:
            provider_status = "failed"
        else:
            provider_status = "processing"

        return {
            "provider_status": provider_status,
            "channel": channel,
            "metadata": metadata,
            "message": message,
            "response": response
        }



    def get(self, request, reference):
        api_client = authenticate_client(request)

        try:
            tx = Transaction.objects.select_related(
                "merchant", "api_client"
            ).get(reference=reference)

            engine = PaymentRouteEngine(client=api_client)

            credentials = engine.get_provider_credentials(
                tx.preferred_provider
            )

            if tx.preferred_provider == "paystack":
                paystack_data = self.__paystack__(tx.reference, credentials)

                metadata = paystack_data["metadata"]
                provider_status = paystack_data["provider_status"]
                channel = paystack_data["channel"]
                message = paystack_data["message"]
                response = paystack_data["response"]

            if tx.preferred_provider == "flutterwave":
                flutterwave_data = self.__flutterwave__(tx.reference, credentials)

                metadata = flutterwave_data["metadata"]
                provider_status = flutterwave_data["provider_status"]
                channel = flutterwave_data["channel"]
                message = flutterwave_data["message"]
                response = flutterwave_data["response"]

            with db_transaction.atomic():

                if provider_status == "success":
                    tx.status = STATUS.SUCCESS
                    tx.channel = channel
                    tx.metadata = metadata
                    tx.completed_at = timezone.now()

                elif provider_status in ["failed", "abandoned"]:
                    tx.status = STATUS.FAILED
                    tx.completed_at = timezone.now()

                tx.message = message

                tx.save(update_fields=[
                    "status",
                    "channel",
                    "metadata",
                    "message",
                    "completed_at",
                    "updated_at"
                ])

            return success_response(
                status_code=200,
                message="Verification requested",
                data=response
            )

        except Transaction.DoesNotExist:
            
            return error_response(
                status_code=400,
                message="Transaction not found",
                errors="Transaction not found"
            )

        except Exception as e:

            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )




