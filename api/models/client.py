import uuid
import secrets
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cryptography.fernet import Fernet
from merchants.models import Merchant

fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)

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
    client_secret = models.CharField(max_length=128, editable=False)
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
        prefix = "pit"
        self.client_id = f"{prefix}_{self.environment}_{secrets.token_hex(8)}"

        raw_secret = f"pit_sk_{self.environment}_{secrets.token_urlsafe(32)}"

        encrypted_secret = fernet.encrypt(raw_secret.encode()).decode()
        self.client_secret = encrypted_secret

        self.save()

        print(f"RAW SECRET: {raw_secret}")
        return raw_secret
        

    def get_decrypted_secret(self):
        return fernet.decrypt(self.client_secret.encode()).decode()
    
    def verify_secret(self, raw_secret):
        try:
            stored_secret = self.get_decrypted_secret()
            return secrets.compare_digest(stored_secret, raw_secret)
        except Exception:
            return False

    def masked_secret(self):
        try:
            secret = self.get_decrypted_secret()
            return f"{secret[:12]}****{secret[-4:]}"
        except Exception:
            return "Invalid"