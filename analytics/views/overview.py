from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from transactions.models import Transaction, STATUS
from analytics.models import ProviderPerformance
from analytics.serializers import ProviderPerformanceSerializer
from modules.core.response import success_response, error_response
from modules.utils.transactions import TransactionUtils


class OverviewView(APIView):
    """
    Analytics endpoint for:
    - Transaction metrics
    - Provider performance
    - Provider success graph
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # -------------------------
        # Transaction Metrics
        # -------------------------

        qs = Transaction.objects.all()
        total_transactions = qs.count()
        successful_tx = qs.filter(status=STATUS.SUCCESS).count()
        failed_tx = qs.filter(status=STATUS.FAILED).count()
        total_value = qs.filter(status=STATUS.SUCCESS).aggregate(
            total=Sum("amount")
        )["total"] or 0

        success_rate = 0
        if total_transactions > 0:
            success_rate = round((successful_tx / total_transactions) * 100, 2)

        transaction_data = {
            "total_transactions": total_transactions,
            "successful_transactions": successful_tx,
            "failed_transactions": failed_tx,
            "success_rate": f"{success_rate}%",
            "total_value": total_value,
        }

        performances = ProviderPerformance.objects.all()
        performance_serializer = ProviderPerformanceSerializer(performances, many=True)

        # provider = request.query_params.get("provider")
        graph_data = None
        graph_data = TransactionUtils.success_rate_per_4hours()

        return success_response(
            data={
                "transactions": transaction_data,
                "provider_performance": performance_serializer.data,
                "provider_success_graph": graph_data
            },
            message="Overview retrieved successfully",
            status_code=status.HTTP_200_OK
        )


class TransactionAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        qs = Transaction.objects.all()

        total_transactions = qs.count()
        successful_tx = qs.filter(status=STATUS.SUCCESS).count()
        failed_tx = qs.filter(status=STATUS.FAILED).count()
        total_value = qs.filter(status=STATUS.SUCCESS).aggregate(
            total=Sum("amount")
        )["total"] or 0

        success_rate = 0
        if total_transactions > 0:
            success_rate = round((successful_tx / total_transactions) * 100, 2)

        data = {
            "total_transactions": total_transactions,
            "successful_transactions": successful_tx,
            "failed_transactions": failed_tx,
            "success_rate": f"{success_rate}%",
            "total_value": total_value,
        }

        return success_response(
            data=data,
            message="Transaction analytics fetched successfully",
            status_code=status.HTTP_200_OK
        )