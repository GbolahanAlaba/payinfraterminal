# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from analytics.models import ProviderPerformance
from analytics.serializers import ProviderPerformanceSerializer
from modules.core.response import success_response
from modules.utils.transactions import TransactionUtils

class ProviderPerformanceView(APIView):
    """
    GET endpoint to return provider performance stats
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        performances = ProviderPerformance.objects.all()
        serializer = ProviderPerformanceSerializer(performances, many=True)
        return success_response(
            data=serializer.data,
            message="Provider performance stats retrieved successfully", 
            status_code=status.HTTP_200_OK
        )
    

class ProviderSuccessGraphView(APIView):
    permission_classes = []

    def get(self, request):
        provider = request.query_params.get("provider")
        if not provider:
            return Response({"error": "provider query param required"}, status=400)
        
        data = TransactionUtils.success_rate_per_4hours(provider)
        return success_response(
            data={"graph_data": data},
            message="Success graph data retrieved successfully",
            status_code=status.HTTP_200_OK
        )