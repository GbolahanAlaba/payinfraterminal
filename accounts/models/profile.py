import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models.account import AccountType
from accounts.models.user import User


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        db_index=True,
    )

    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )

    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        default=Gender.MALE,
        db_index=True,
    )

    image = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    profile_id = models.CharField(
        max_length=9,
        unique=True,
        editable=False,
        db_index=True,
    )

    pin = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile of {(self.user.full_name or self.user.email).strip()}"

    def save(self, *args, **kwargs):
        from modules.utils.utils import AccountUtils

        # Generate unique profile_id if not set
        if not self.profile_id:
            self.profile_id = self._generate_unique_profile_id()

        super().save(*args, **kwargs)

    def _generate_unique_profile_id(self):
        """Helper method to generate a unique profile ID."""
        from modules.utils.utils import AccountUtils

        while True:
            pid = AccountUtils.generate_profile_id()
            if not Profile.objects.filter(profile_id=pid).exists():
                return pid