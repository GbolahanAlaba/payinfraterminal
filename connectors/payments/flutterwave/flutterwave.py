import logging
from .charges import FlutterwaveCharges
from .customers import FlutterwaveCustomers
from .payment_methods import FlutterwavePaymentMethods
from .payments import FlutterwavePayments
from .transfers import FlutterwaveTransfers

# Set up logging
logger = logging.getLogger(__name__)

class FlutterwaveClient:
    """
    Main Flutterwave client that provides access to all Flutterwave services.
    """

    def __init__(self, secret_key: str, is_sandbox: bool = True):
        """
        Initialize the Flutterwave client.

        Args:
            secret_key: Flutterwave secret key
            is_sandbox: Whether to use sandbox environment
        """
        self.secret_key = secret_key
        self.is_sandbox = is_sandbox
        
        logger.info(f"Initializing FlutterwaveClient - Secret Key Length: {len(secret_key) if secret_key else 0}, Is Sandbox: {is_sandbox}")
        
        # Initialize service modules
        self.charges = FlutterwaveCharges(secret_key, is_sandbox)
        self.customers = FlutterwaveCustomers(secret_key, is_sandbox)
        self.payment_methods = FlutterwavePaymentMethods(secret_key, is_sandbox)
        self.payments = FlutterwavePayments(secret_key, is_sandbox)
        self.transfers = FlutterwaveTransfers(secret_key, is_sandbox)

    def __repr__(self):
        env = "sandbox" if self.is_sandbox else "production"
        return f"FlutterwaveClient(environment={env})"
