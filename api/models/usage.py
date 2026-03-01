from django.db import models
from django.utils import timezone
from .client import APIClient


class APIUsageRecord(models.Model):
    """Records each API request for billing / analytics"""
    client = models.ForeignKey(APIClient, on_delete=models.CASCADE, related_name="usage_records")
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    request_count = models.IntegerField()
    status_code = models.IntegerField()
    response_time = models.FloatField(help_text="Response time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "API Usage Record"
        verbose_name_plural = "API Usage Records"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.client_name} | {self.endpoint} | {self.status_code}"