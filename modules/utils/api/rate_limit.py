# merchants/utils/rate_limit.py
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from api.models import APIRateLimit
from payinfraterminal.merchants.models.account_key import MerchantAccountKey  # your model linked to Merchant or API client

class RateLimitExceeded(Exception):
    """Exception when API client exceeds rate limit."""
    pass

def check_api_rate_limit(secret_key: str):
    """
    Checks if an API client using `api_key` has exceeded their rate limit.
    Raises RateLimitExceeded if limits are breached.
    """

    # Get rate limit configuration for the API key / merchant
    try:
        secret = MerchantAccountKey.objects.get(secret_key=secret_key)
        rate_limit = APIRateLimit.objects.get(merchant=secret.merchant)
    except (MerchantAccountKey.DoesNotExist, APIRateLimit.DoesNotExist):
        # No configured limits => allow by default
        return True

    now = timezone.now()

    # Cache keys for tracking usage
    cache_keys = {
        'minute': f"rate_limit:{secret_key}:minute",
        'hour': f"rate_limit:{secret_key}:hour",
        'day': f"rate_limit:{secret_key}:day",
    }

    # Get current counts from cache
    counts = {k: cache.get(v, 0) for k, v in cache_keys.items()}

    # Check limits
    if counts['minute'] >= rate_limit.requests_per_minute + rate_limit.burst_allowance:
        raise RateLimitExceeded("Requests per minute exceeded")
    if counts['hour'] >= rate_limit.requests_per_hour:
        raise RateLimitExceeded("Requests per hour exceeded")
    if counts['day'] >= rate_limit.requests_per_day:
        raise RateLimitExceeded("Requests per day exceeded")

    # Increment counts in cache
    cache.set(cache_keys['minute'], counts['minute'] + 1, timeout=60)
    cache.set(cache_keys['hour'], counts['hour'] + 1, timeout=3600)
    cache.set(cache_keys['day'], counts['day'] + 1, timeout=86400)

    return True