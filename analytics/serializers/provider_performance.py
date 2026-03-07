# serializers.py
from rest_framework import serializers
from analytics.models import ProviderPerformance

class ProviderPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderPerformance
        fields = [
            "provider",
            "success_rate",
            "failure_rate",
            "avg_latency",
            "total_transactions",
            "successful_transactions",
            "failed_transactions",
            "last_updated",
        ]