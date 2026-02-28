import uuid
import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from merchants.models import Merchant


class APIClientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class Environment(models.TextChoices):
    LIVE = "live", _("Live")
    SANDBOX = "sandbox", _("Sandbox")


class APIClient(models.Model):
    """Represents a merchant consuming your API via JWT or API token"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default="yeurir")
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="api_clients")
    client_name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=64, unique=True, editable=False)
    client_secret = models.CharField(max_length=128, editable=False)  # hashed
    environment = models.CharField(max_length=20, choices=Environment.choices, default=Environment.LIVE)
    status = models.CharField(max_length=20, choices=APIClientStatus.choices, default=APIClientStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "API Client"
        verbose_name_plural = "API Clients"
        unique_together = ("merchant", "client_name")

    def __str__(self):
        return f"{self.client_name} ({self.merchant.business_name})"

    def generate_credentials(self):
        """Generates a new client_id and client_secret (hashed)"""
        prefix = "pit"  # PayInfraTerminal prefix
        self.client_id = f"{prefix}_{self.environment}_{secrets.token_hex(8)}"
        raw_secret = secrets.token_urlsafe(32)
        self.client_secret = make_password(raw_secret)
        self.save()
        return raw_secret

    def verify_secret(self, raw_secret):
        """Verify a raw secret against the stored hashed secret"""
        return check_password(raw_secret, self.client_secret)