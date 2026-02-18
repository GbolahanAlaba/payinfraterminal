from django.db import models
from merchants.models import Merchant


class MerchantTransaction(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="transactions")
    provider = models.CharField(max_length=50)  # Paystack, Flutterwave, OPay
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=5, default="NGN")
    status = models.CharField(max_length=50)  # pending, success, failed
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)