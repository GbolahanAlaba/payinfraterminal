from random import randint
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from merchants.models import Merchant

class STATUS(models.TextChoices):
    PROCESSING = "processing", _("Processing")
    SUCCESS = "success", _("Success")
    FAILED = "failed", _("Failed")
    RETRYING = "retrying", _("Retrying")
    ABANDONED = "abandoned", _("Abandoned")

class TRANSACTION_SOURCE(models.TextChoices):
    API = "api", _("API")
    PAYMENT_LINK = "payment_link", _("Payment Link")
    CHECKOUT = "checkout", _("Checkout")
    POS = "pos", _("POS")


class TRANSACTION_TYPE(models.TextChoices):
    COLLECTION = "collection", _("Collection")
    PAYOUT = "payout", _("Payout")
    REFUND = "refund", _("Refund")


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE.choices,
        default=TRANSACTION_TYPE.COLLECTION
    )
    transaction_source = models.CharField(
        max_length=20, 
        choices=TRANSACTION_SOURCE.choices,
        default=TRANSACTION_SOURCE.API
    )
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, blank=True, null=True, default="NGN")

    channel = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        default="card", 
        help_text="Payment channel used, e.g. card, bank_transfer, ussd"
    )

    reference = models.CharField(max_length=100, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.PROCESSING)
    
    preferred_provider = models.CharField(max_length=50, blank=True, null=True)
    final_provider = models.CharField(max_length=50, blank=True, null=True)

    latency = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Latency in milliseconds for the transaction processing"
    )

    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


    def generate_transaction_id():
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"

    def create_transaction(
        merchant,
        amount,
        reference,
        customer_email=None,
        customer_phone=None,
        currency="NGN",
        channel="card",
        transaction_type=None,
        transaction_source=None,
        preferred_provider=None,
        final_provider=None,
        latency=None,
        metadata=None,
    ):
        """
        Create a transaction record.
        """

        transaction = Transaction.objects.create(
            transaction_id=Transaction.generate_transaction_id(),
            merchant=merchant,
            amount=amount,
            reference=reference,
            customer_email=customer_email,
            customer_phone=customer_phone,
            currency=currency,
            channel=channel,
            transaction_type=transaction_type or TRANSACTION_TYPE.COLLECTION,
            transaction_source=transaction_source or TRANSACTION_SOURCE.API,
            preferred_provider=preferred_provider,
            final_provider=final_provider,
            latency=latency,
            metadata=metadata or {},
            message="Transaction initialized",
        )

        return transaction
    

class TransactionAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="attempts")
    
    provider = models.CharField(max_length=50)
    provider_reference = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.PROCESSING)
    
    fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    response = models.JSONField(default=dict, blank=True)
    
    retry_count = models.IntegerField(default=0)

    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ["attempted_at"]
    
    def __str__(self):
        return f"{self.transaction.transaction_id} - {self.provider} - {self.status}"

    def create_transaction_attempt(transaction, provider, provider_reference=None, response=None):
        attempt = TransactionAttempt.objects.create(
            transaction=transaction,
            provider=provider,
            provider_reference=provider_reference,
            response=response or {},
            status="pending",
            retry_count=0
        )

        return attempt