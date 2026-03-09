from django.urls import path
from api.views import ProcessPaymentAPIView
from api.views import SetupClientProviderAPIView, RegenerateAPIKeysView, TestAPIView, UpdateWebhookURLView

urlpatterns = [
    path("client/<uuid:client_id>/regenerate-keys/", RegenerateAPIKeysView.as_view(), name="regenerate-api-keys"),
    path("client/<uuid:client_id>/webhook-url/", UpdateWebhookURLView.as_view(), name="update-webhook-url"),
    path("initiate-payment/", ProcessPaymentAPIView.as_view(), name="initiate-payment"),
    path("client-provider/setup/", SetupClientProviderAPIView.as_view(), name="setup-client-provider"),
    path("test-api/", TestAPIView.as_view(), name="test-api"),
]