import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models.user import User


class VerificationPurpose(models.TextChoices):
    EMAIL = "email", _("Email Verification")
    PASSWORD = "password", _("Password Reset")
    PIN = "pin", _("PIN")


class OTP(models.Model):
    EXPIRY_MINUTES = 10  # Centralized expiry duration

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otps",
    )

    code = models.CharField(max_length=6)

    purpose = models.CharField(
        max_length=30,
        choices=VerificationPurpose.choices,
        default=VerificationPurpose.EMAIL,
    )

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "purpose"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.get_purpose_display()} OTP for {self.user.email}"

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)

    @property
    def is_expired(self):
        return self.is_used or timezone.now() > self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])