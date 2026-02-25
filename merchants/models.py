import uuid
import secrets
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modules.utils.utils import AccountUtils
from accounts.models import User


class Merchant(models.Model):
    MERCHANT_TYPE_CHOICES = [
        ("sole proprietor", "Sole Proprietor"),
        ("llc", "Limited Liability Company"),
        ("corporation", "Corporation"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="merchants")
    merchant_id = models.CharField(max_length=10, unique=True, editable=False, db_index=True)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    merchant_type = models.CharField(max_length=20, choices=MERCHANT_TYPE_CHOICES, default="sole proprietor")
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "merchant"
        verbose_name_plural = "merchants"

    def __str__(self):
        return f"{self.business_name} ({self.user.full_name})"

    def save(self, *args, **kwargs):
        if not self.merchant_id:
            while True:
                mid = AccountUtils.generate_merchant_id()
                if not Merchant.objects.filter(merchant_id=mid).exists():
                    self.merchant_id = mid
                    break
        super().save(*args, **kwargs)


class MerchantAccountKey(models.Model):
    PROVIDER_CHOICES = [
        ("live", "Live"),
        ("sandbox", "Sandbox"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name="account_keys")
    account_id = models.CharField(max_length=255, blank=True, null=True)
    merchant_api_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    environment = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="live")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "merchant account key"
        verbose_name_plural = "merchant account keys"

    def __str__(self):
        return f"Account key for {self.merchant.business_name}"

    def save(self, *args, **kwargs):
        if not self.merchant_api_key:
            self.merchant_api_key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    

class MerchantAPIKey(models.Model):
    PROVIDER_CHOICES = [
        ("paystack", "Paystack"),
        ("flutterwave", "Flutterwave"),
        ("opay", "OPay"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="api_keys")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    secret_key = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("merchant", "provider")
        verbose_name = "merchant API key"
        verbose_name_plural = "merchant API keys"

    def __str__(self):
        return f"{self.provider} key for {self.merchant.business_name}"
    

class KYCDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="kyc_docs")
    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to="kyc_documents/")
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)