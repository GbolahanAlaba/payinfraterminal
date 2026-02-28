import uuid
from django.db import models
from django.utils import timezone
from accounts.models import User
from merchants.models import Merchant


class APIClientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class APIClient(models.Model):
    """Represents a merchant or user consuming your API via a token"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="api_clients")
    client_name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)  # JWT secret or API token
    status = models.CharField(max_length=20, choices=APIClientStatus.choices, default=APIClientStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "API Client"
        verbose_name_plural = "API Clients"

    def __str__(self):
        return f"{self.client_name} ({self.merchant.business_name})"