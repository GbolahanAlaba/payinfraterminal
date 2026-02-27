import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from .merchant import Merchant


class KYCDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="kyc_documents",
    )

    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to="kyc_documents/")
    verified = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("KYC Document")
        verbose_name_plural = _("KYC Documents")
        ordering = ("-uploaded_at",)

    def __str__(self):
        return f"{self.document_type} - {self.merchant.business_name}"