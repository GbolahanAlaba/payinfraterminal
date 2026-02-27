import uuid
import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from .merchant import Merchant


class Environment(models.TextChoices):
    LIVE = "live", _("Live")
    SANDBOX = "sandbox", _("Sandbox")


class MerchantAccountKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    merchant = models.OneToOneField(
        Merchant,
        on_delete=models.CASCADE,
        related_name="account_keys",
    )

    account_id = models.CharField(max_length=255, blank=True, null=True)
    merchant_api_key = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )

    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.LIVE,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Merchant Account Key")
        verbose_name_plural = _("Merchant Account Keys")

    def __str__(self):
        return f"{self.merchant.business_name} ({self.environment})"

    def save(self, *args, **kwargs):
        if not self.merchant_api_key:
            self.merchant_api_key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)