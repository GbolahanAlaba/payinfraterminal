from django.contrib import admin
from .models import Transaction, TransactionAttempt


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
        "status",
        "channel",
        "final_provider",
        "created_at",
    )

    list_filter = (
        "status",
        "channel",
        "transaction_type",
        "transaction_source",
        "final_provider",
        "created_at",
    )

    search_fields = (
        "transaction_id",
        "reference",
        "customer_email",
        "customer_phone",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "completed_at",
    )

    inlines = [TransactionAttemptInline]


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
        "provider_reference",
        "transaction__transaction_id",
    )