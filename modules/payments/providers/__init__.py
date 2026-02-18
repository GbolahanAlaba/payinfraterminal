from django.db import transaction

from support.models import TechPartner
from modules.payments.providers.paystack import PaystackProvider

def load_payment_providers():
    """
    Dynamically load payment providers based on database entries.
    """
    providers = TechPartner.objects.all()
    provider_map = {}

    if providers.filter(provider__iexact="paystack", is_active=True).exists():
        provider_map["paystack"] = PaystackProvider

    # Uncomment if you add these providers later:
    # if providers.filter(name__iexact="flutterwave").exists():
    #     provider_map["flutterwave"] = FlutterwaveProvider
    #
    # if providers.filter(name__iexact="fincra").exists():
    #     provider_map["fincra"] = FincraProvider

    return provider_map

PAYMENT_PROVIDERS = load_payment_providers()


def register_payment_provider(provider_name, client_class):
    PAYMENT_PROVIDERS[provider_name] = client_class


def sync_payment_providers(sender=None, **kwargs):
    """
    Sync payment providers from the database.

    Args:
        sender: The sender of the signal.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    with transaction.atomic():
        registered_name = set(PAYMENT_PROVIDERS.keys())

        existing_providers = TechPartner.objects.all()
        existing_name = set(provider.provider for provider in existing_providers)

        to_add = registered_name - existing_name
        to_remove = existing_name - registered_name

        TechPartner.objects.filter(name__in=to_remove).delete()

        for provider_name in to_add:
            TechPartner.objects.create(name=provider_name)
