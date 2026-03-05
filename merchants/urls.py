# merchants/urls.py
from django.urls import path
from merchants.views import MerchantViewSet
from merchants.views import ToggleMerchantModeView

merchant_update = MerchantViewSet.as_view({
    'patch': 'partial_update'
})

urlpatterns = [
    path('merchant/<uuid:pk>/update/', MerchantViewSet.as_view({'patch': 'partial_update'}), name='merchant-update'),
    path("switch/toggle-merchant-mode/", ToggleMerchantModeView.as_view(), name="toggle-merchant-mode"),
]