import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from .client import APIClient


class PaymentProvider(models.TextChoices):
    PAYSTACK = "paystack", _("Paystack")
    FLUTTERWAVE = "flutterwave", _("Flutterwave")
    OPAY = "opay", _("OPay")


class ProviderAPIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name="provider_keys",
    )

    provider = models.CharField(
        max_length=50,
        choices=PaymentProvider.choices,
    )

    secret_key = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("client", "provider")
        verbose_name = _("Provider API Key")
        verbose_name_plural = _("Provider API Keys")

    def __str__(self):
        return f"{self.get_provider_display()} key for {self.client.merchant.business_name}"