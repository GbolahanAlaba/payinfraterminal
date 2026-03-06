"""
GTP Service Business Logic Configuration
Centralized configuration for GTP-specific business rules
"""
from django.conf import settings


class GTPConfig:
    """
    GTP Service configuration accessor
    Provides clean interface to GTP settings
    """
    
    # Service Info
    SERVICE_NAME = getattr(settings, 'GTP_SERVICE_NAME', 'Guaranteed Trust Payments')
    API_VERSION = getattr(settings, 'GTP_API_VERSION', 'v1')
    ENABLED = getattr(settings, 'GTP_SERVICE_ENABLED', True)
    
    @classmethod
    @property
    def service_version(cls):
        """Get service version from settings"""
        return getattr(settings, 'APP_VERSION', '1.0.0')
    
    @classmethod
    @property
    def service_environment(cls):
        """Get service environment from settings"""
        return getattr(settings, 'SERVER_ENV', 'development')
    
    # API Configuration
    API_KEY_PREFIX = getattr(settings, 'GTP_API_KEY_PREFIX', 'gtp_')
    API_KEY_LENGTH = getattr(settings, 'GTP_API_KEY_LENGTH', 32)
    API_KEY_EXPIRY_DAYS = getattr(settings, 'GTP_API_KEY_EXPIRY_DAYS', 365)
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = getattr(settings, 'GTP_RATE_LIMIT_ENABLED', True)
    DEFAULT_RATE_LIMIT_PER_MINUTE = getattr(settings, 'GTP_DEFAULT_RATE_LIMIT_PER_MINUTE', 60)
    DEFAULT_RATE_LIMIT_PER_HOUR = getattr(settings, 'GTP_DEFAULT_RATE_LIMIT_PER_HOUR', 1000)
    DEFAULT_RATE_LIMIT_PER_DAY = getattr(settings, 'GTP_DEFAULT_RATE_LIMIT_PER_DAY', 10000)
    
    # Logging
    LOG_ALL_REQUESTS = getattr(settings, 'GTP_LOG_ALL_REQUESTS', True)
    LOG_REQUEST_BODY = getattr(settings, 'GTP_LOG_REQUEST_BODY', False)
    LOG_RETENTION_DAYS = getattr(settings, 'GTP_LOG_RETENTION_DAYS', 90)
    
    # Idempotency
    IDEMPOTENCY_ENABLED = getattr(settings, 'GTP_IDEMPOTENCY_ENABLED', True)
    IDEMPOTENCY_TTL_HOURS = getattr(settings, 'GTP_IDEMPOTENCY_TTL_HOURS', 24)
    
    # DCP Integration
    DCP_ENABLED = getattr(settings, 'GTP_DCP_ENABLED', True)
    DCP_TIMEOUT = getattr(settings, 'GTP_DCP_TIMEOUT', 30)
    DCP_MAX_RETRIES = getattr(settings, 'GTP_DCP_MAX_RETRIES', 3)
    DCP_RETRY_BACKOFF = getattr(settings, 'GTP_DCP_RETRY_BACKOFF', 0.3)
    
    # Circuit Breaker
    DCP_CIRCUIT_BREAKER_ENABLED = getattr(settings, 'GTP_DCP_CIRCUIT_BREAKER_ENABLED', True)
    DCP_CIRCUIT_BREAKER_THRESHOLD = getattr(settings, 'GTP_DCP_CIRCUIT_BREAKER_THRESHOLD', 5)
    DCP_CIRCUIT_BREAKER_TIMEOUT = getattr(settings, 'GTP_DCP_CIRCUIT_BREAKER_TIMEOUT', 60)
    
    # Webhooks
    WEBHOOK_ENABLED = getattr(settings, 'GTP_WEBHOOK_ENABLED', True)
    WEBHOOK_TIMEOUT = getattr(settings, 'GTP_WEBHOOK_TIMEOUT', 30)
    WEBHOOK_MAX_RETRIES = getattr(settings, 'GTP_WEBHOOK_MAX_RETRIES', 7)
    WEBHOOK_RETRY_DELAYS = getattr(settings, 'GTP_WEBHOOK_RETRY_DELAYS', [1, 2, 4, 8, 16, 32, 64])
    WEBHOOK_SIGNATURE_ALGORITHM = getattr(settings, 'GTP_WEBHOOK_SIGNATURE_ALGORITHM', 'sha256')
    
    # Billing
    PLATFORM_FEE_MONTHLY = getattr(settings, 'GTP_PLATFORM_FEE_MONTHLY', 500.00)
    PLATFORM_FEE_CURRENCY = getattr(settings, 'GTP_PLATFORM_FEE_CURRENCY', 'CAD')
    BILLING_WEEK_START_DAY = getattr(settings, 'GTP_BILLING_WEEK_START_DAY', 0)
    BILLING_RESET_TIME = getattr(settings, 'GTP_BILLING_RESET_TIME', '00:00:00')
    
    # Transaction Fee Tiers
    DEFAULT_PAYIN_TIERS = getattr(settings, 'GTP_DEFAULT_PAYIN_TIERS', [])
    DEFAULT_PAYOUT_CAD_TIERS = getattr(settings, 'GTP_DEFAULT_PAYOUT_CAD_TIERS', [])
    DEFAULT_PAYOUT_INTL_TIERS = getattr(settings, 'GTP_DEFAULT_PAYOUT_INTL_TIERS', [])
    
    # Security
    FIELD_ENCRYPTION_KEY = getattr(settings, 'GTP_FIELD_ENCRYPTION_KEY', '')
    KEY_ROTATION_DATE = getattr(settings, 'GTP_KEY_ROTATION_DATE', '')
    KEY_ROTATION_DAYS = getattr(settings, 'GTP_KEY_ROTATION_DAYS', 90)
    API_KEY_HASH_ALGORITHM = getattr(settings, 'GTP_API_KEY_HASH_ALGORITHM', 'bcrypt')
    BCRYPT_COST_FACTOR = getattr(settings, 'GTP_BCRYPT_COST_FACTOR', 12)
    ENFORCE_TLS_13 = getattr(settings, 'GTP_ENFORCE_TLS_13', True)
    
    # Monitoring
    METRICS_ENABLED = getattr(settings, 'GTP_METRICS_ENABLED', True)
    ERROR_TRACKING_ENABLED = getattr(settings, 'GTP_ERROR_TRACKING_ENABLED', True)
    
    # Sandbox
    SANDBOX_ENABLED = getattr(settings, 'GTP_SANDBOX_ENABLED', True)
    SANDBOX_DATA_RETENTION_DAYS = getattr(settings, 'GTP_SANDBOX_DATA_RETENTION_DAYS', 30)
    
    # Feature Flags
    FEATURES = getattr(settings, 'GTP_FEATURES', {})
    
    @classmethod
    def is_feature_enabled(cls, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return cls.FEATURES.get(feature_name, False)
    
    @classmethod
    def get_tier_config(cls, transaction_type: str) -> list:
        """Get tier configuration for a transaction type"""
        tier_map = {
            'payin': cls.DEFAULT_PAYIN_TIERS,
            'payout_cad': cls.DEFAULT_PAYOUT_CAD_TIERS,
            'payout_intl': cls.DEFAULT_PAYOUT_INTL_TIERS,
        }
        return tier_map.get(transaction_type, [])
