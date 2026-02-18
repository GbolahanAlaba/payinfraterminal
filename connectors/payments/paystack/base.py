import requests
import logging
log = logging.getLogger('my_logger')

class PaystackBase:
    def __init__(self, secret_key):
        if not secret_key:
            raise ValueError("A Paystack secret key is required")

        self.secret_key = secret_key
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
        self.base_url = "https://api.paystack.co"
        self.timeout = 30

    def _make_request(self, method, endpoint, params=None, data=None, json=None):
        """
        Make an HTTP request to the Paystack API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint (str): API endpoint (e.g., "/transaction/initialize")
            params (dict, optional): Query parameters for the request
            data (dict, optional): Form data for the request
            json (dict, optional): JSON payload for the request

        Returns:
            dict: Parsed JSON response from the API

        Raises:
            requests.exceptions.RequestException: For network-related issues
            ValueError: If the response cannot be parsed as JSON
            Exception: For Paystack API errors
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # 🔥 THIS is what you need
                log.error("Paystack error response: %s", response.text)
                raise

            # Attempt to parse the response as JSON
            try:
                response_data = response.json()
            except ValueError:
                raise ValueError(f"Invalid JSON response: {response.text}")

            # Check for Paystack-specific errors
            if not response_data.get("status", False):
                raise Exception(
                    f"Paystack API error: {response_data.get('message', 'Unknown error')}",
                )

            return response_data

        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {e!s}")

    def get(self, endpoint, params=None):
        """Shortcut for making GET requests"""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint, json=None, data=None):
        """Shortcut for making POST requests"""
        return self._make_request("POST", endpoint, json=json, data=data)

    def put(self, endpoint, json=None, data=None):
        """Shortcut for making PUT requests"""
        return self._make_request("PUT", endpoint, json=json, data=data)

    def delete(self, endpoint, params=None):
        """Shortcut for making DELETE requests"""
        return self._make_request("DELETE", endpoint, params=params)
