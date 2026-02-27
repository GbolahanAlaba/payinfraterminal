import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from modules.utils.utils import AccountUtils


class MerchantType(models.TextChoices):
    SOLE_PROPRIETOR = "sole_proprietor", _("Sole Proprietor")
    LLC = "llc", _("Limited Liability Company")
    CORPORATION = "corporation", _("Corporation")


class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="merchants",
    )

    merchant_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        db_index=True,
    )

    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)

    merchant_type = models.CharField(
        max_length=20,
        choices=MerchantType.choices,
        default=MerchantType.SOLE_PROPRIETOR,
    )

    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Merchant")
        verbose_name_plural = _("Merchants")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.business_name} ({self.user.full_name})"

    def save(self, *args, **kwargs):
        if not self.merchant_id:
            self.merchant_id = self._generate_unique_merchant_id()
        super().save(*args, **kwargs)

    def _generate_unique_merchant_id(self):
        while True:
            mid = AccountUtils.generate_merchant_id()
            if not Merchant.objects.filter(merchant_id=mid).exists():
                return mid