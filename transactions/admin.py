from django.contrib import admin
from .models import Transaction, CollectionTransaction, TransactionAttempt


class CollectionTransactionInline(admin.StackedInline):
    model = CollectionTransaction
    extra = 0
    can_delete = False
    readonly_fields = (
        "preferred_provider",
        "final_provider",
        "provider_reference",
        "payment_link",
        "latency",
        "metadata",
    )

class TransactionAttemptInline(admin.TabularInline):
    model = TransactionAttempt
    extra = 0
    readonly_fields = (
        "provider",
        "provider_reference",
        "status",
        "fee",
        "retry_count",
        "attempted_at",
        "completed_at",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "merchant",
        "amount",
        "currency",
        "transaction_type",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "transaction_type",
        "currency",
        "created_at",
    )

    search_fields = (
        "transaction_id",
        "reference",
        "merchant__business_name",
    )

    readonly_fields = (
        "transaction_id",
        "created_at",
        "updated_at",
        "completed_at",
    )

    inlines = [
        CollectionTransactionInline,
        TransactionAttemptInline
    ]

    ordering = ("-created_at",)


@admin.register(CollectionTransaction)
class CollectionTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "amount",
        "currency",
        "preferred_provider",
        "final_provider",
        "channel",
        "created_at",
    )

    search_fields = (
        "transaction__transaction_id",
        "customer_email",
        "customer_phone",
    )

    list_filter = (
        "channel",
        "preferred_provider",
        "final_provider",
    )

    readonly_fields = (
        "transaction",
        "created_at",
        "updated_at",
        "completed_at",
    )


@admin.register(TransactionAttempt)
class TransactionAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "provider",
        "status",
        "retry_count",
        "attempted_at",
    )

    list_filter = (
        "provider",
        "status",
    )

    search_fields = (
        "transaction__transaction_id",
        "provider_reference",
    )

    readonly_fields = (
        "attempted_at",
        "completed_at",
        "response",
    )