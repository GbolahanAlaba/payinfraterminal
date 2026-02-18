"""
Flutterwave Integration Example

This example demonstrates how to use the Flutterwave payment provider
with the TITAA backend payment system.
"""

import uuid
from titaa.services.payments.flutterwave import FlutterwaveClient
from titaa.services.payments.flutterwave.exceptions import (
    FlutterwaveAPIException,
    FlutterwaveValidationException,
)
from titaa.payments.providers.flutterwave import FlutterwaveProvider


def example_flutterwave_usage():
    """Example of how to use the Flutterwave payment provider."""

    # Initialize the provider (uses settings configuration)
    provider = FlutterwaveProvider()

    try:
        # Initialize a payment transaction
        payment_response = provider.initialize_transaction(
            email="customer@example.com",
            amount=50000,  # Amount in kobo (NGN 500.00)
            currency="NGN",
            name="John Doe",
            phone_number="+2348012345678",
            reference="TITAA-ORDER-123456",
            metadata={
                "order_id": "ORDER-12345",
                "customer_id": "CUST-67890"
            }
        )

        print("Payment initialized successfully!")
        print(f"Status: {payment_response.get('status')}")
        
        if payment_response.get("status") == "success":
            clean_data = provider.clean_init_data(payment_response)
            print(f"Payment URL: {clean_data.get('payment_url')}")
            print(f"Reference: {clean_data.get('reference')}")
            print(f"Amount: {clean_data.get('amount')} {clean_data.get('currency')}")

        return payment_response

    except FlutterwaveAPIException as e:
        print(f"API error: {e.message} (Status: {e.status_code})")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None


def example_direct_api_usage():
    """Example of using the Flutterwave API client directly."""

    # Initialize the client
    secret_key = "FLWSECK_TEST-your-secret-key-here"
    client = FlutterwaveClient(secret_key=secret_key, is_sandbox=True)

    try:
        # Create a customer
        customer_response = client.customers.create_customer(
            email="john.doe@example.com",
            name="John Doe",
            phone="+2348012345678"
        )
        
        print("Customer created:")
        print(f"Customer ID: {customer_response['data']['id']}")
        print(f"Email: {customer_response['data']['email']}")

        # Create a card payment method (example data)
        payment_method_response = client.payment_methods.create_card_payment_method(
            customer_id=customer_response["data"]["id"],
            card_number="4111111111111111",
            expiry_month="12",
            expiry_year="25",
            cvv="123",
            cardholder_name="John Doe"
        )
        
        print("Payment method created:")
        print(f"Payment Method ID: {payment_method_response['data']['id']}")

        # Create a charge
        charge_response = client.charges.create_charge(
            amount=100.0,  # NGN 100.00
            currency="NGN",
            customer_id=customer_response["data"]["id"],
            payment_method_id=payment_method_response["data"]["id"],
            reference="TXN-" + str(uuid.uuid4())[:8].upper(),
            redirect_url="https://example.com/callback"
        )

        print("Charge created:")
        print(f"Charge ID: {charge_response['data']['id']}")
        print(f"Status: {charge_response['data']['status']}")
        
        # Get next action (usually a redirect URL for completion)
        next_action = charge_response['data'].get('next_action', {})
        if next_action.get('type') == 'redirect_url':
            redirect_url = next_action['redirect_url']['url']
            print(f"Complete payment at: {redirect_url}")

        return charge_response

    except FlutterwaveValidationException as e:
        print(f"Validation error: {e.message}")
        if e.validation_errors:
            print("Validation errors:", e.validation_errors)
    except FlutterwaveAPIException as e:
        print(f"API error: {e.message} (Status: {e.status_code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def example_payment_verification():
    """Example of verifying a payment."""
    
    provider = FlutterwaveProvider()
    
    # Verify payment by charge ID or reference
    charge_id_or_reference = "chg_Hq4oBRTJ4r"  # or "TITAA-ORDER-123456"
    
    try:
        verification_response = provider.verify_transaction(charge_id_or_reference)
        
        if verification_response.get("status") == "success":
            data = verification_response["data"]
            print(f"Payment verification successful:")
            print(f"Status: {data['status']}")
            print(f"Amount: {data['amount']} {data['currency']}")
            print(f"Reference: {data['reference']}")
            print(f"Customer: {data['customer']['email']}")
        else:
            print(f"Verification failed: {verification_response.get('message')}")
            
    except Exception as e:
        print(f"Verification error: {str(e)}")


def example_webhook_handling():
    """Example of how webhooks are handled."""
    
    # Sample webhook payload from Flutterwave
    webhook_payload = {
        "data": {
            "amount": 2500,
            "created_datetime": 1735116842.116,
            "currency": "NGN",
            "customer": {
                "email": "customer@example.com",
                "id": "cus_csm0pcQim4",
                "name": "John Doe",
                "phone": "+2348012345678"
            },
            "id": "chg_Hq4oBRTJ4r",
            "reference": "TITAA-ORDER-123456",
            "status": "succeeded"
        },
        "id": "wbk_W5p6ktwU0jQ8RO4By860",
        "timestamp": 1735116884019,
        "type": "charge.completed"
    }
    
    # This is what happens when a webhook is received
    print("Webhook received:")
    print(f"Event Type: {webhook_payload['type']}")
    print(f"Reference: {webhook_payload['data']['reference']}")
    print(f"Status: {webhook_payload['data']['status']}")
    print(f"Amount: {webhook_payload['data']['amount']} {webhook_payload['data']['currency']}")
    
    # The webhook handler would:
    # 1. Validate the signature
    # 2. Mark the payment as successful in the database
    # 3. Update the order status
    # 4. Send notifications if needed


if __name__ == "__main__":
    print("=== Flutterwave Provider Usage ===")
    example_flutterwave_usage()

    print("\n=== Direct API Usage ===")
    example_direct_api_usage()

    print("\n=== Payment Verification ===")
    example_payment_verification()

    print("\n=== Webhook Handling ===")
    example_webhook_handling()