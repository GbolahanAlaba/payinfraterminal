import uuid
import secrets
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from merchants.models import Merchant

class Environment(models.TextChoices):
    LIVE = "live", "Live"
    SANDBOX = "Sandbox", "sandbox"


class APIClientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"

fernet = Fernet(settings.FERNET_SECRET_KEY)

class APIClient(models.Model):
    """
    Represents a merchant consuming your API
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="api_clients"
    )

    client_name = models.CharField(max_length=255)

    client_public_key = models.CharField(
        max_length=64,
        unique=True,
        editable=False
    )

    client_secret_key = models.TextField(editable=False)

    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.LIVE
    )

    status = models.CharField(
        max_length=20,
        choices=APIClientStatus.choices,
        default=APIClientStatus.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "API Client"
        verbose_name_plural = "API Clients"
        unique_together = ("merchant", "client_name")

    def __str__(self):
        return f"{self.client_name} ({self.merchant.business_name})"


    def generate_credentials(self):
        """
        Generates client_id and encrypted client_secret.
        Returns raw_secret (ONLY show once to merchant).
        """

        prefix = "pit_pk"
        self.client_public_key = f"{prefix}_{self.environment}_{secrets.token_hex(8)}"
        raw_secret = f"pit_sk_{self.environment}_{secrets.token_urlsafe(32)}"

        # encrypted_secret = fernet.encrypt(raw_secret.encode()).decode()
        self.client_secret_key = raw_secret #encrypted_secret

        self.save()

        return raw_secret


    def _decrypt_secret(self):
        try:
            return fernet.decrypt(self.client_secret.encode()).decode()
        except InvalidToken:
            return None

    def verify_secret(self, raw_secret: str) -> bool:
        """
        Securely verify secret using constant time comparison
        """

        try:
            stored_secret = self._decrypt_secret()
            if not stored_secret:
                return False

            return secrets.compare_digest(stored_secret, raw_secret)
        except Exception:
            return False