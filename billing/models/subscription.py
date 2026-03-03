import uuid
from django.db import models
from merchants.models import Merchant
from .plan import Plan

class MerchantSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name="merchant_subscriptions")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Merchant Subscription"
        verbose_name_plural = "Merchant Subscriptions"

    def __str__(self):
        return f"{self.merchant.business_name} - {self.plan.name}"