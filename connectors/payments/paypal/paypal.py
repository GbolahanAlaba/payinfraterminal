import logging

from .payments import PayPalPayments
from .refunds import PayPalRefunds

logger = logging.getLogger(__name__)


class PayPalClient:
    """
    Main PayPal client that provides access to all PayPal services.

    Mirrors FlutterwaveClient exactly:
      - Receives credentials in __init__
      - Exposes service modules as attributes (payments, refunds)
      - Each module is an independent PayPalAPIClient subclass

    Usage:
        client = PayPalClient(
            client_id="AXxx...",
            client_secret="EKxx...",
            is_sandbox=True,
        )
        order = client.payments.create_payment(...)
        refund = client.refunds.refund_capture(capture_id, amount="10.00", currency="USD")
    """

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        """
        Initialize the PayPal client.

        Args:
            client_id:     PayPal REST app Client ID.
            client_secret: PayPal REST app Client Secret.
            is_sandbox:    True → sandbox, False → live/production.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox

        logger.info(
            "Initializing PayPalClient - Client ID Prefix: %s, Is Sandbox: %s",
            client_id[:6] if client_id else "INVALID",
            is_sandbox,
        )

        # Service modules — same pattern as FlutterwaveClient
        self.payments = PayPalPayments(client_id, client_secret, is_sandbox)
        self.refunds = PayPalRefunds(client_id, client_secret, is_sandbox)

    def __repr__(self):
        env = "sandbox" if self.is_sandbox else "production"
        return f"PayPalClient(environment={env})"
