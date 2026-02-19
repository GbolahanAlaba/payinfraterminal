import json
import logging
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from modules.services.payment_services import PaymentService



class PaymentViewSets(viewsets.ViewSet):
    permission_classes = [AllowAny]

    payment_provider = PaymentService()

    def make_payment(self, request):
        amount = request.data.get('amount')
        reference = request.data.get('reference')
        provider = request.data.get('provider')
        environment = request.data.get('environment')
        
        if not amount:
            return Response({"status": "failed", "message": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        amount = Decimal(str(amount))
        result = self.payment_provider.initialize_payment(
            email=request.data.get("email"),
            amount=amount,
            net_amount=amount,
            reference=reference if reference else None,
        )

        status_code = 200 if result.get("status") == "success" else 400
        return Response(result, status=status_code)
    
    def verify_payment(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"status": "failed", "message": "Reference is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.payment_provider.verify_payment(reference=reference)
        status_code = 200 if result.get("status") == "success" else 400
        return Response(result, status=status_code)
    