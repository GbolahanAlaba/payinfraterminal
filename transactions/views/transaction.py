from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from transactions.models import Transaction
from transactions.serializers import (
    TransactionCreateSerializer,
    TransactionResponseSerializer,
)
from modules.core.response import success_response, error_response

class CreateTransactionView(APIView):

    def post(self, request):

        serializer = TransactionCreateSerializer(data=request.data)

        if serializer.is_valid():

            transaction = serializer.save(
                merchant=request.user.merchant
            )

            response = TransactionResponseSerializer(transaction)

            return Response(response.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, reference):

        if reference:
            try:
                transaction = Transaction.objects.get(reference=reference)
            except Transaction.DoesNotExist:
                return error_response(
                    message="Transaction not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        
        transaction = Transaction.objects.all().order_by("-created_at")
        serializer = TransactionResponseSerializer(transaction)

        return success_response(
            data=serializer.data,
            message="Transaction retrieved successfully",
            status_code=200,
            
            )

class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        transactions = Transaction.objects.all().order_by("-created_at")

        serializer = TransactionResponseSerializer(transactions, many=True)

        return success_response(
            data=serializer.data,
            message="Transactions retrieved successfully",
        )

class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):

        try:
            transaction = Transaction.objects.get(reference=reference)
        except Transaction.DoesNotExist:
            return error_response(
                message="Transaction not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = TransactionResponseSerializer(transaction)

        return success_response(
            data=serializer.data,
            message="Transaction retrieved successfully",
            status_code=200,
        )

    