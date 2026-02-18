from typing import Dict, Any, Optional
from .base import FlutterwaveAPIClient
from .exceptions import FlutterwaveValidationException


class FlutterwavePaymentMethods(FlutterwaveAPIClient):
    """Handle Flutterwave payment method operations."""

    def create_card_payment_method(
        self,
        customer_id: str,
        card_number: str,
        expiry_month: str,
        expiry_year: str,
        cvv: str,
        cardholder_name: Optional[str] = None,
        billing_address: Optional[Dict[str, str]] = None,
        device_fingerprint: Optional[str] = None,
        client_ip: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a card payment method.

        Args:
            customer_id: ID of the customer
            card_number: Card number
            expiry_month: Card expiry month (MM format)
            expiry_year: Card expiry year (YY format)
            cvv: Card CVV/CVC
            cardholder_name: Name on the card
            billing_address: Billing address details
            device_fingerprint: Device fingerprint for fraud detection
            client_ip: Client IP address
            meta: Additional metadata
            **kwargs: Additional payment method data

        Returns:
            API response containing payment method details

        Raises:
            FlutterwaveAPIException: If payment method creation fails
        """
        payload = {
            "type": "card",
            "customer_id": customer_id,
            "card": {
                "number": card_number,
                "expiry_month": expiry_month,
                "expiry_year": expiry_year,
                "cvv": cvv
            }
        }

        # Add optional card fields
        if cardholder_name:
            payload["card"]["cardholder_name"] = cardholder_name
        
        if billing_address:
            payload["card"]["billing_address"] = billing_address

        # Add optional top-level fields
        if device_fingerprint:
            payload["device_fingerprint"] = device_fingerprint
        
        if client_ip:
            payload["client_ip"] = client_ip
            
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        return self.post("/payment-methods", data=payload)

    def create_mobile_money_payment_method(
        self,
        customer_id: str,
        phone_number: str,
        network: str,
        country_code: str = "234",
        device_fingerprint: Optional[str] = None,
        client_ip: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a mobile money payment method.

        Args:
            customer_id: ID of the customer
            phone_number: Mobile phone number
            network: Mobile network (e.g., "MTN", "Airtel")
            country_code: Country code (defaults to "234" for Nigeria)
            device_fingerprint: Device fingerprint for fraud detection
            client_ip: Client IP address
            meta: Additional metadata
            **kwargs: Additional payment method data

        Returns:
            API response containing payment method details

        Raises:
            FlutterwaveAPIException: If payment method creation fails
        """
        payload = {
            "type": "mobile_money",
            "customer_id": customer_id,
            "mobile_money": {
                "phone_number": phone_number,
                "network": network,
                "country_code": country_code
            }
        }

        # Add optional fields
        if device_fingerprint:
            payload["device_fingerprint"] = device_fingerprint
        
        if client_ip:
            payload["client_ip"] = client_ip
            
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        return self.post("/payment-methods", data=payload)

    def create_bank_transfer_payment_method(
        self,
        customer_id: str,
        account_number: str,
        bank_code: str,
        account_name: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        client_ip: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a bank transfer payment method.

        Args:
            customer_id: ID of the customer
            account_number: Bank account number
            bank_code: Bank code
            account_name: Account holder name
            device_fingerprint: Device fingerprint for fraud detection
            client_ip: Client IP address
            meta: Additional metadata
            **kwargs: Additional payment method data

        Returns:
            API response containing payment method details

        Raises:
            FlutterwaveAPIException: If payment method creation fails
        """
        payload = {
            "type": "bank_transfer",
            "customer_id": customer_id,
            "bank_transfer": {
                "account_number": account_number,
                "bank_code": bank_code
            }
        }

        # Add optional bank transfer fields
        if account_name:
            payload["bank_transfer"]["account_name"] = account_name

        # Add optional fields
        if device_fingerprint:
            payload["device_fingerprint"] = device_fingerprint
        
        if client_ip:
            payload["client_ip"] = client_ip
            
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        return self.post("/payment-methods", data=payload)

    def list_payment_methods(
        self,
        customer_id: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List payment methods with optional filtering.

        Args:
            customer_id: Filter by customer ID
            type: Filter by payment method type (card, mobile_money, bank_transfer)
            page: Page number (minimum 1, defaults to 1)
            size: Number of items per page (10-50, defaults to 10)
            **kwargs: Additional query parameters

        Returns:
            API response containing list of payment methods

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
        if customer_id:
            params["customer_id"] = customer_id
        if type:
            params["type"] = type

        # Add any additional parameters
        params.update(kwargs)

        return self.get("/payment-methods", params=params)

    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Get details of a specific payment method.

        Args:
            payment_method_id: The ID of the payment method to retrieve

        Returns:
            API response containing payment method details

        Raises:
            FlutterwaveAPIException: If payment method retrieval fails
        """
        return self.get(f"/payment-methods/{payment_method_id}")

    def update_payment_method(
        self,
        payment_method_id: str,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing payment method.

        Args:
            payment_method_id: The ID of the payment method to update
            meta: New metadata
            **kwargs: Additional fields to update

        Returns:
            API response containing updated payment method details

        Raises:
            FlutterwaveAPIException: If payment method update fails
        """
        payload = {}

        # Add fields to update
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        if not payload:
            raise FlutterwaveValidationException("At least one field must be provided for update")

        return self.put(f"/payment-methods/{payment_method_id}", data=payload)

    def delete_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Delete a payment method.

        Args:
            payment_method_id: The ID of the payment method to delete

        Returns:
            API response confirming deletion

        Raises:
            FlutterwaveAPIException: If payment method deletion fails
        """
        return self.delete(f"/payment-methods/{payment_method_id}")

    def get_customer_payment_methods(
        self,
        customer_id: str,
        type: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Get all payment methods for a specific customer.

        Args:
            customer_id: The customer ID
            type: Filter by payment method type
            page: Page number
            size: Number of items per page

        Returns:
            API response containing customer's payment methods

        Raises:
            FlutterwaveAPIException: If retrieval fails
        """
        return self.list_payment_methods(
            customer_id=customer_id,
            type=type,
            page=page,
            size=size
        )