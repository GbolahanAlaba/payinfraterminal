from django.urls import path
from api.views.payment import ProcessPaymentAPIView
from api.views import SetupClientProviderAPIView

urlpatterns = [
    path("process-payment/", ProcessPaymentAPIView.as_view(), name="process-payment"),
    path("client-provider/setup/", SetupClientProviderAPIView.as_view(), name="setup-client-provider")
]