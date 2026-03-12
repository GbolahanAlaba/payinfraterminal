"""
URL patterns for PayPal integration.

Include in your project urls.py::

    path("api/payments/paypal/", include("paypal.urls")),
"""
from django.urls import path

from .views import CaptureOrderView, CreateOrderView, GetOrderView, RefundView, WebhookView

app_name = "paypal"

urlpatterns = [
    path("orders/", CreateOrderView.as_view(), name="create-order"),
    path("orders/<str:paypal_order_id>/", GetOrderView.as_view(), name="get-order"),
    path("orders/<str:paypal_order_id>/capture/", CaptureOrderView.as_view(), name="capture-order"),
    path("refunds/", RefundView.as_view(), name="refund"),
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
