import json
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from cryptography.fernet import Fernet
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

class ClientProvider(models.Model):

    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name="providers"
    )

    provider = models.CharField(max_length=50, choices=PaymentProvider.choices,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "provider")

    def __str__(self):
        return f"{self.client.merchant.business_name} - {self.client.environment} - {self.provider}"

class ClientProviderCredential(models.Model):
    client_provider = models.OneToOneField(
        ClientProvider,
        on_delete=models.CASCADE,
        related_name="credentials"
    )

    # Encrypted JSON blob containing keys/tokens/certs/etc.
    credentials = models.JSONField()
    credential_type = models.CharField(
        max_length=50,
        default="api_key"
    )

    is_encrypted = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credentials for {self.client_provider}"
    
    @property
    def _fernet(self):
        return Fernet(settings.CREDENTIAL_ENCRYPTION_KEY.encode())

    def encrypt_credentials(self, raw_data: dict) -> str:
        json_data = json.dumps(raw_data)
        encrypted = self._fernet.encrypt(json_data.encode())
        return encrypted.decode()

    def decrypt_credentials(self) -> dict:
        if not self.credentials:
            return {}

        decrypted = self._fernet.decrypt(
            self.credentials.encode()
        )
        return json.loads(decrypted.decode())


    def save(self, *args, **kwargs):
        if self.credentials and not self.is_encrypted:
            self.credentials = self.encrypt_credentials(self.credentials)
            self.is_encrypted = True

        super().save(*args, **kwargs)

