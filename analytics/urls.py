# urls.py
from django.urls import path
from .views import HealthView

urlpatterns = [
    path("health-check/", HealthView.as_view()),
]