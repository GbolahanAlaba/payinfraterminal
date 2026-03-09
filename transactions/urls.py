from django.urls import path
from .views import CreateTransactionView, TransactionDetailView, TransactionListView


urlpatterns = [
    path("", TransactionListView.as_view(), name="transaction-list"),
    path("<uuid:id>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("transactions/create/", CreateTransactionView.as_view(), name="create-transaction",),
]