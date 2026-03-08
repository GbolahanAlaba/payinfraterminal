# urls.py
from django.urls import path
from .views import (HealthView, 
        ProviderPerformanceView, 
        ProviderSuccessGraphView, 
        OverviewView)

urlpatterns = [
    path("health-check/", HealthView.as_view()),
    path("overview/", OverviewView.as_view(), name="success-rate-graph"),
    path("provider-performance/", ProviderPerformanceView.as_view(), name="provider-performance"),
    path("success-rate/", ProviderSuccessGraphView.as_view(), name="success-rate-graph"),
]
