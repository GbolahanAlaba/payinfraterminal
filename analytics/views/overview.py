from django.db.models import Sum,  Count, Q, F, FloatField, ExpressionWrapper

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

        # performances = ProviderPerformance.objects.all()
        # performance_serializer = ProviderPerformanceSerializer(performances, many=True)

        provider_qs = (
        qs.values("preferred_provider")  # group by provider
        .annotate(
            total_transactions=Count("id"),
            successful_transactions=Count("id", filter=Q(status=STATUS.SUCCESS)),
            failed_transactions=Count("id", filter=Q(status=STATUS.FAILED)),
            success_rate=ExpressionWrapper(
                F("successful_transactions") * 100.0 / F("total_transactions"),
                output_field=FloatField()
            )
        )
        )

        provider_performance = []
        for p in provider_qs:
            provider_performance.append({
                "provider": p["preferred_provider"],
                "total_transactions": p["total_transactions"],
                "successful_transactions": p["successful_transactions"],
                "failed_transactions": p["failed_transactions"],
                "success_rate": f"{round(p['success_rate'], 2)}%",
                "status": "good" if p["success_rate"] >= 95 else "average" if p["success_rate"] >= 80 else "poor"
            })

        # provider = request.query_params.get("provider")
        graph_data = None
        graph_data = TransactionUtils.success_rate_per_month(year=None)

        return success_response(
            data={
                "transactions": transaction_data,
                "provider_performance": provider_performance,
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