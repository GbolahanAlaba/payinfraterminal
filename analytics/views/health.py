
import time
import shutil
import psutil
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.core.cache import cache
from django.conf import settings
# from payinfra.celery import celery_app
import requests
from modules.core.response import success_response
from modules.core.config import GTPConfig
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from modules.core.response import success_response


class HealthView(APIView):

    def get(self, request):
        """
        Health check endpoint for monitoring and load balancers.
        
        Returns service status and basic health metrics.
        No authentication required.
        """
        status = "healthy"
        checks = {}

        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            status = "unhealthy"

        # Check Redis/cache connectivity
        try:
            key = "health:check"
            cache.set(key, "ok", timeout=5)
            result = cache.get(key)
            checks["cache"] = "ok" if result == "ok" else "error"
        except Exception as e:
            checks["cache"] = f"error: {str(e)}"
            status = "degraded"

        # Disk Space Check
        try:
            disk = shutil.disk_usage("/")
            free_percent = (disk.free / disk.total) * 100
            checks["disk_space_free_percent"] = round(free_percent, 2)

            if free_percent < 10:  # Alert if low
                status = "degraded"
        except Exception as e:
            checks["disk"] = f"error: {str(e)}"

        # Memory Check
        try:
            memory = psutil.virtual_memory()
            checks["memory_available_percent"] = round(memory.available / memory.total * 100, 2)
        except Exception as e:
            checks["memory"] = f"error: {str(e)}"

        
        # External Service Health Example
        try:
            external_url = getattr(settings, "EXTERNAL_HEALTH_URL", None)

            if external_url:
                response = requests.get(external_url, timeout=3)
                checks["external_service"] = (
                    "ok" if response.status_code == 200 else "unhealthy"
                )
        except Exception as e:
            checks["external_service"] = f"error: {str(e)}"
            status = "degraded"

        response_data = {
            "status": status,
            "service": "gtp",
            "version": getattr(settings, "API_VERSION", "unknown"),
            "timestamp": int(time.time()),
            "checks": checks,
        }

        status_code = 200 if status == "healthy" else 503
        return success_response(data=response_data, status_code=status_code)


    @csrf_exempt
    @require_http_methods(["GET"])
    def status(request):
        """
        Detailed status endpoint with service information.
        No authentication required.
        """
        from django.conf import settings
        from modules.core.config import GTPConfig
        
        return JsonResponse({
            "service": "Guaranteed Trust Payments (GTP)",
            "version": getattr(settings, 'APP_VERSION', '1.0.0'),
            "environment": getattr(settings, 'SERVER_ENV', 'development'),
            "api_version": "v1",
            "endpoints": {
                "base": "/gtp/v1",
                "health": "/gtp/v1/health",
                "status": "/gtp/v1/status",
                "docs": "/gtp/v1/docs",
            },
            "features": {
                "rate_limiting": GTPConfig.RATE_LIMIT_ENABLED,
                "idempotency": GTPConfig.IDEMPOTENCY_ENABLED,
                "webhooks": True,
                "sandbox": True,
            },
        })
