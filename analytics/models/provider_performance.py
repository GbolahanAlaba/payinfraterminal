import uuid
from django.db import models


class ProviderPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50)
    success_rate = models.FloatField(default=0)
    failure_rate = models.FloatField(default=0)
    avg_latency = models.FloatField(default=0)
    total_transactions = models.IntegerField(default=0)
    successful_transactions = models.IntegerField(default=0)
    failed_transactions = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)