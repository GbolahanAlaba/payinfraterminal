import logging
from typing import Dict, Any, Optional, List
from .base import FlutterwaveAPIClient
from .exceptions import FlutterwaveValidationException

# Set up logging
logger = logging.getLogger(__name__)

class FlutterwaveCharges(FlutterwaveAPIClient):
    """Handle Flutterwave charge operations."""

    def __init__(self, secret_key: str, is_sandbox: bool = True):
        """
        Initialize the Flutterwave charges service.

        Args:
            secret_key: Flutterwave secret key
            is_sandbox: Whether to use sandbox environment
        """
        logger.info(f"Initializing FlutterwaveCharges - Secret Key Length: {len(secret_key) if secret_key else 0}, Is Sandbox: {is_sandbox}")
        super().__init__(secret_key, is_sandbox)

    def create_charge(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        reference: str,
        redirect_url: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        recurring: bool = False,
        order_id: Optional[str] = None,
        authorization: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a charge.

        Args:
            amount: Payment amount in decimals (minimum 0.01)
            currency: ISO 4217 currency code
            customer_id: ID of the customer
            payment_method_id: ID of the payment method
            reference: Custom identifier to track the transaction (6-42 chars, must be unique)
            redirect_url: URL to redirect to after payment
            meta: Additional metadata
            recurring: Whether this is a recurring charge
            order_id: ID of the order (for preauth captures)
            authorization: Authorization object for payment
            **kwargs: Additional parameters

        Returns:
            API response containing charge details

        Raises:
            FlutterwaveAPIException: If charge creation fails
        """
        # Validate required parameters
        if amount < 0.01:
            raise FlutterwaveValidationException("Amount must be at least 0.01")
        
        if not (6 <= len(reference) <= 42):
            raise FlutterwaveValidationException("Reference must be between 6 and 42 characters")

        payload = {
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "payment_method_id": payment_method_id,
            "reference": reference,
            "recurring": recurring
        }

        # Add optional parameters
        if redirect_url:
            payload["redirect_url"] = redirect_url
        
        if meta:
            payload["meta"] = meta
            
        if order_id:
            payload["order_id"] = order_id
            
        if authorization:
            payload["authorization"] = authorization

        # Add any additional kwargs
        payload.update(kwargs)

        return self.post("/charges", data=payload)

    def list_charges(
        self,
        status: Optional[str] = None,
        reference: Optional[str] = None,
        to_date: Optional[str] = None,
        from_date: Optional[str] = None,
        customer_id: Optional[str] = None,
        virtual_account_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        order_id: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List charges with optional filtering.

        Args:
            status: Filter by charge status (e.g., 'succeeded')
            reference: Filter by transaction reference
            to_date: End date for filtering (ISO 8601 format)
            from_date: Start date for filtering (ISO 8601 format)
            customer_id: Filter by customer ID
            virtual_account_id: Filter by virtual account ID
            payment_method_id: Filter by payment method ID
            order_id: Filter by order ID
            page: Page number (minimum 1, defaults to 1)
            size: Number of items per page (10-50, defaults to 10)

        Returns:
            API response containing list of charges

        Raises:
            FlutterwaveAPIException: If listing fails
        """
        # Validate parameters
        if page < 1:
            raise FlutterwaveValidationException("Page must be at least 1")
        
        if not (10 <= size <= 50):
            raise FlutterwaveValidationException("Size must be between 10 and 50")

        params = {
            "page": page,
            "size": size
        }

        # Add optional filters
        if status:
            params["status"] = status
        if reference:
            params["reference"] = reference
        if to_date:
            params["to"] = to_date
        if from_date:
            params["from"] = from_date
        if customer_id:
            params["customer_id"] = customer_id
        if virtual_account_id:
            params["virtual_account_id"] = virtual_account_id
        if payment_method_id:
            params["payment_method_id"] = payment_method_id
        if order_id:
            params["order_id"] = order_id

        # Add any additional parameters
        params.update(kwargs)

        return self.get("/charges", params=params)

    def get_charge(self, charge_id: str) -> Dict[str, Any]:
        """
        Get details of a specific charge.

        Args:
            charge_id: The ID of the charge to retrieve

        Returns:
            API response containing charge details

        Raises:
            FlutterwaveAPIException: If charge retrieval fails
        """
        return self.get(f"/charges/{charge_id}")

    def verify_charge(self, charge_id: str) -> Dict[str, Any]:
        """
        Verify a charge by ID. This is an alias for get_charge 
        but more explicitly indicates verification intent.

        Args:
            charge_id: The ID of the charge to verify

        Returns:
            API response containing charge verification details

        Raises:
            FlutterwaveAPIException: If verification fails
        """
        return self.get_charge(charge_id)

    def verify_charge_by_reference(self, reference: str) -> Dict[str, Any]:
        """
        Verify a charge by transaction reference.

        Args:
            reference: The transaction reference to verify

        Returns:
            API response containing charge verification details

        Raises:
            FlutterwaveAPIException: If verification fails
        """
        # List charges filtered by reference
        response = self.list_charges(reference=reference, size=1)
        
        charges = response.get("data", [])
        if not charges:
            raise FlutterwaveValidationException(f"No charge found with reference: {reference}")
        
        # Return the first (and should be only) charge
        return {
            "status": "success",
            "message": "Charge verified successfully",
            "data": charges[0]
        }

    def create_otp_authorization(self, otp: str) -> Dict[str, str]:
        """
        Create OTP authorization object for charge creation.

        Args:
            otp: The OTP code

        Returns:
            Authorization object for OTP
        """
        return {
            "type": "otp",
            "otp": otp
        }

    def create_pin_authorization(self, pin: str) -> Dict[str, str]:
        """
        Create PIN authorization object for charge creation.

        Args:
            pin: The PIN code

        Returns:
            Authorization object for PIN
        """
        return {
            "type": "pin",
            "pin": pin
        }

    def create_external_3ds_authorization(self, redirect_url: str) -> Dict[str, str]:
        """
        Create 3DS authorization object for charge creation.

        Args:
            redirect_url: URL to redirect for 3DS authentication

        Returns:
            Authorization object for 3DS
        """
        return {
            "type": "external_3ds",
            "redirect_url": redirect_url
        }