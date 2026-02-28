from django.urls import path
from api.views.payment import ProcessPaymentAPIView

urlpatterns = [
    path("process-payment/", ProcessPaymentAPIView.as_view(), name="process-payment"),
]