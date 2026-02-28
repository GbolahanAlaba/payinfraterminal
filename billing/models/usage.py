import uuid
from django.db import models
from merchants.models import Merchant

class UsageRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="usage_records")
    transaction_count = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    month = models.DateField()  # e.g., first day of the month

    class Meta:
        verbose_name = "Usage Record"
        verbose_name_plural = "Usage Records"

    def __str__(self):
        return f"{self.merchant.business_name} - {self.month}"