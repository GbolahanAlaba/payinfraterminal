from django.db.models import Sum,  Count, Q, F, FloatField, ExpressionWrapper
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

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
        qs.values("provider")  # group by provider
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
                "provider": p["provider"],
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

class OverviewGraphView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                description="Year to filter monthly data (e.g., 2026). Defaults to current year if not provided.",
                required=False,
                type=int
            ),
        ],
        examples=[
            OpenApiExample(
                "Sample Response",
                value={
                    "status": 200,
                    "message": "Graph data for 2026",
                    "monthly_data": [
                        {
                            "month": "January",
                            "month_start": "2026-01-01T00:00:00Z",
                            "total_transactions": 12,
                            "successful_transactions": 10,
                            "success_rate": 83.33
                        },
                        {
                            "month": "February",
                            "month_start": "2026-02-01T00:00:00Z",
                            "total_transactions": 0,
                            "successful_transactions": 0,
                            "success_rate": 0
                        }
                    ]
                },
                response_only=True,
            )
        ],
        responses={
            200: dict,
            400: {"error": "Invalid year parameter"}
        },
        description="Retrieve monthly transaction success rate for a given year. Includes all 12 months even if there are zero transactions."
    )
    def get(self, request):
        year_param = request.query_params.get("year")
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return error_response(
                status_code=400,
                message="Invalid year value",
                errors="Invalid year value",
            )
        
        monthly_data = TransactionUtils.success_rate_per_month(year)

        now = timezone.now()
        year_d = int(year_param) if year_param else now.year
        return success_response(
            status_code=200,
            message=f"Graph data for {year_d}",
            data=monthly_data,
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