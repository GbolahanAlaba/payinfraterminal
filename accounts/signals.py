import secrets
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, AccountType
from merchants.models import Merchant
from api.models import APIClient, APIRateLimit
from billing.models import MerchantSubscription, Plan


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        acct_type = AccountType.objects.filter(name="Business").first()
        Profile.objects.create(user=instance, account_type=acct_type)


@receiver(post_save, sender=Merchant)
def setup_merchant_related(sender, instance: Merchant, created, **kwargs):
    if not created:
        return

    # 1. Create API Clients for sandbox & live
    from api.models.client import Environment
    api_clients = []
    for env in [Environment.SANDBOX, Environment.LIVE]:
        client = APIClient.objects.create(
            merchant=instance,
            client_name=f"{instance.business_name} ({env})",
            environment=env
        )
        raw_secret = client.generate_credentials()
        api_clients.append(client)

    # 2. Create default rate limits
    for api_client in api_clients:
        APIRateLimit.objects.create(
            client=api_client,
            tier="free",
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=1000,
            burst_allowance=10
        )

    # 3. Create default subscription
    plan = Plan.objects.filter(name='Free').first()
    MerchantSubscription.objects.create(
        merchant=instance,
        plan=plan,
        is_active=True
    )

    # 4. Optionally, generate JWT token for API access
    refresh = RefreshToken.for_user(instance.user)
    print(f"Merchant JWT (access): {refresh.access_token}")
    print(f"Merchant JWT (refresh): {refresh}")