"""
Flutterwave Payment Service Integration

This package provides a comprehensive integration with Flutterwave's payment API,
including support for charges, customers, payments, and payment methods.

Main Components:
- FlutterwaveClient: Main client for all Flutterwave operations
- FlutterwaveCharges: Handle charge operations
- FlutterwaveCustomers: Handle customer operations  
- FlutterwavePayments: Handle payment link creation and verification
- FlutterwavePaymentMethods: Handle payment method operations
- FlutterwaveAPIException: Exception handling

Usage:
    from titaa.services.payments.flutterwave import FlutterwaveClient
    
    client = FlutterwaveClient(secret_key="your_secret_key", is_sandbox=True)
    
    # Create customer
    customer = client.customers.create_customer(
        email="customer@example.com",
        name="John Doe"
    )
    
    # Create charge
    charge = client.charges.create_charge(
        amount=100.0,
        currency="NGN",
        customer_id=customer["data"]["id"],
        payment_method_id="pmd_xxxx",
        reference="unique_ref_123"
    )
"""

from .flutterwave import FlutterwaveClient
from .charges import FlutterwaveCharges
from .customers import FlutterwaveCustomers
from .payment_methods import FlutterwavePaymentMethods
from .payments import FlutterwavePayments
from .exceptions import (
    FlutterwaveException,
    FlutterwaveAPIException,
    FlutterwaveAuthenticationException,
    FlutterwaveValidationException,
    FlutterwaveNotFoundException,
    FlutterwaveRateLimitException,
    FlutterwaveNetworkException,
    FlutterwaveWebhookException,
)

__all__ = [
    "FlutterwaveClient",
    "FlutterwaveCharges", 
    "FlutterwaveCustomers",
    "FlutterwavePaymentMethods",
    "FlutterwavePayments",
    "FlutterwaveException",
    "FlutterwaveAPIException",
    "FlutterwaveAuthenticationException",
    "FlutterwaveValidationException",
    "FlutterwaveNotFoundException",
    "FlutterwaveRateLimitException",
    "FlutterwaveNetworkException",
    "FlutterwaveWebhookException",
]

__version__ = "1.0.0"
