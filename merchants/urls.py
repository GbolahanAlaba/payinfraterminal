# merchants/urls.py
from django.urls import path
from merchants.views import MerchantViewSet

merchant_update = MerchantViewSet.as_view({
    'patch': 'partial_update'
})

urlpatterns = [
    path('merchant/<uuid:pk>/update/', MerchantViewSet.as_view({'patch': 'partial_update'}), name='merchant-update'),
]