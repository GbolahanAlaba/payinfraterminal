from django.urls import path
from api.views import ProcessPaymentAPIView
from api.views import SetupClientProviderAPIView, RegenerateAPIKeysView, TestAPIView

urlpatterns = [
    path("client/<uuid:client_id>/regenerate-keys/", RegenerateAPIKeysView.as_view(), name="regenerate-api-keys"),
    path("initiate-payment/", ProcessPaymentAPIView.as_view(), name="initiate-payment"),
    path("client-provider/setup/", SetupClientProviderAPIView.as_view(), name="setup-client-provider"),
    path("test-api/", TestAPIView.as_view(), name="test-api"),
]