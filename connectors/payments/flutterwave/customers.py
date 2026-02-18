from typing import Dict, Any, Optional
from .base import FlutterwaveAPIClient
from .exceptions import FlutterwaveValidationException


class FlutterwaveCustomers(FlutterwaveAPIClient):
    """Handle Flutterwave customer operations."""

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new customer.

        Args:
            email: Customer's email address (required)
            name: Customer's full name
            phone: Customer's phone number
            address: Customer's address
            meta: Additional metadata for the customer
            **kwargs: Additional customer data

        Returns:
            API response containing customer details

        Raises:
            FlutterwaveAPIException: If customer creation fails
        """
        payload = {
            "email": email
        }

        # Add optional fields
        if name:
            payload["name"] = name
        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        return self.post("/customers", data=payload)

    def list_customers(
        self,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List customers with optional filtering.

        Args:
            page: Page number (minimum 1, defaults to 1)
            size: Number of items per page (10-50, defaults to 10)
            email: Filter by customer email
            name: Filter by customer name
            **kwargs: Additional query parameters

        Returns:
            API response containing list of customers

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
        if email:
            params["email"] = email
        if name:
            params["name"] = name

        # Add any additional parameters
        params.update(kwargs)

        return self.get("/customers", params=params)

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get details of a specific customer.

        Args:
            customer_id: The ID of the customer to retrieve

        Returns:
            API response containing customer details

        Raises:
            FlutterwaveAPIException: If customer retrieval fails
        """
        return self.get(f"/customers/{customer_id}")

    def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing customer.

        Args:
            customer_id: The ID of the customer to update
            email: New email address
            name: New name
            phone: New phone number
            address: New address
            meta: New metadata
            **kwargs: Additional fields to update

        Returns:
            API response containing updated customer details

        Raises:
            FlutterwaveAPIException: If customer update fails
        """
        payload = {}

        # Add fields to update
        if email:
            payload["email"] = email
        if name:
            payload["name"] = name
        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address
        if meta:
            payload["meta"] = meta

        # Add any additional kwargs
        payload.update(kwargs)

        if not payload:
            raise FlutterwaveValidationException("At least one field must be provided for update")

        return self.put(f"/customers/{customer_id}", data=payload)

    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Delete a customer.

        Args:
            customer_id: The ID of the customer to delete

        Returns:
            API response confirming deletion

        Raises:
            FlutterwaveAPIException: If customer deletion fails
        """
        return self.delete(f"/customers/{customer_id}")

    def search_customers(
        self,
        query: str,
        page: int = 1,
        size: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search customers by query string.

        Args:
            query: Search query (email, name, etc.)
            page: Page number (minimum 1, defaults to 1)
            size: Number of items per page (10-50, defaults to 10)
            **kwargs: Additional search parameters

        Returns:
            API response containing search results

        Raises:
            FlutterwaveAPIException: If search fails
        """
        params = {
            "q": query,
            "page": page,
            "size": size
        }

        # Add any additional parameters
        params.update(kwargs)

        return self.get("/customers/search", params=params)

    def get_or_create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get existing customer by email or create a new one.

        Args:
            email: Customer's email address
            name: Customer's name (used if creating)
            phone: Customer's phone (used if creating)
            address: Customer's address (used if creating)
            meta: Customer's metadata (used if creating)
            **kwargs: Additional customer data

        Returns:
            API response containing customer details

        Raises:
            FlutterwaveAPIException: If operation fails
        """
        try:
            # Try to find existing customer by email
            customers_response = self.list_customers(email=email, size=1)
            customers = customers_response.get("data", [])
            
            if customers:
                # Customer exists, return the first one
                return {
                    "status": "success",
                    "message": "Customer found",
                    "data": customers[0]
                }
            else:
                # Customer doesn't exist, create new one
                return self.create_customer(
                    email=email,
                    name=name,
                    phone=phone,
                    address=address,
                    meta=meta,
                    **kwargs
                )
                
        except Exception:
            # If search fails, try to create customer
            # This handles cases where the search endpoint might not work as expected
            return self.create_customer(
                email=email,
                name=name,
                phone=phone,
                address=address,
                meta=meta,
                **kwargs
            )