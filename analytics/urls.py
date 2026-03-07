# urls.py
from django.urls import path
from .views import HealthView, ProviderPerformanceView

urlpatterns = [
    path("health-check/", HealthView.as_view()),
    path("provider-performance/", ProviderPerformanceView.as_view(), name="provider-performance"),
]