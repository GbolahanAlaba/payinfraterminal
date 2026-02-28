import uuid
from django.db import models
from .client import APIClient


class APIRateLimitTier(models.TextChoices):
    FREE = "free", "Free"
    STARTER = "starter", "Starter"
    BASIC = "basic", "Basic"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"
    CUSTOM = "custom", "Custom"

class APIRateLimit(models.Model):
    """
    Rate limiting configuration for merchants using the API
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Merchant Association by Client
    client = models.OneToOneField(
        APIClient,
        on_delete=models.CASCADE,
        related_name="rate_limit",
        help_text="Associated merchant APIClient"
    )
    
    # Tier
    tier = models.CharField(
        max_length=20,
        choices=APIRateLimitTier.choices,
        default=APIRateLimitTier.STARTER,
        db_index=True,
    )
    
    # Limits
    requests_per_minute = models.IntegerField(default=60)
    requests_per_hour = models.IntegerField(default=1000)
    requests_per_day = models.IntegerField(default=10000)
    burst_allowance = models.IntegerField(default=10)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rate Limit"
        verbose_name_plural = "Rate Limits"
        indexes = [
            models.Index(fields=["tier"]),
        ]
    
    def __str__(self):
        return f"{self.client.merchant.business_name} - {self.get_tier_display()}"