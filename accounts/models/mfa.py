# accounts/models/mfa.py

import uuid
from django.db import models
from django.utils import timezone
from accounts.models.user import User

class MFAType(models.TextChoices):
    TOTP = "totp", "TOTP (Authenticator App)"
    SMS = "sms", "SMS OTP"
    EMAIL = "email", "Email OTP"

class MFAStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    DISABLED = "disabled", "Disabled"

class MFADevice(models.Model):
    """
    Multi-Factor Authentication device for a user.
    Can be TOTP, SMS, or Email-based.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_devices")
    type = models.CharField(max_length=20, choices=MFAType.choices)
    status = models.CharField(max_length=20, choices=MFAStatus.choices, default=MFAStatus.PENDING)
    secret = models.CharField(max_length=255, help_text="TOTP secret or token storage")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "MFA Device"
        verbose_name_plural = "MFA Devices"
        unique_together = ("user", "type")  # One active device per type per user

    def __str__(self):
        return f"{self.user.full_name or self.user.email} - {self.get_type_display()}"

    @property
    def is_verified(self):
        return self.verified_at is not None