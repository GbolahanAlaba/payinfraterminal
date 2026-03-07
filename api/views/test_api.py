import logging
from random import randint
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

log = logging.getLogger(__name__)

class TestAPIView(APIView):
    permission_classes = []

    def post(self, request):

        CLIENT_PUBLIC_KEY = "pit_pk_Sandbox_8417456a565be43b"
        CLIENT_SECRET_KEY = "pit_sk_Sandbox_isPUZD1Xlio4jZmTBexYvT1-d6GupSZUVnxaNwoz_bU"
        log.info(CLIENT_PUBLIC_KEY, CLIENT_PUBLIC_KEY)
        
        url = "http://payinfraterminal.onrender.com/v1/api/initiate-payment/"
        log.info(f"Initiating test payment to {url} with payload and headers.")
        payload = {
            "provider": "flutterwave",
            # "provider": "paystack",
            "email": "customer@example.com", 
            "amount": 5000,                    
            "reference": randint(100000, 999999),
            "callback_url": "https://payflow.com/payments/",
            "currency": "USD",
        }

        headers = {
            "Client-Public-Key": CLIENT_PUBLIC_KEY,
            "Client-Secret-Key": CLIENT_SECRET_KEY,
            # "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            log.info(f"Test API Response: {response.status_code} - {response.text}")
            response.raise_for_status()
            data = response.json()
            log.info(f"Transaction Successful: {data}")
            print("Transaction Successful:", data)
            return Response(data, status=response.status_code)

        except requests.exceptions.HTTPError as err:
            print("HTTP error occurred:", err)
            return Response(
                {"error": "HTTP error occurred", "details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except requests.exceptions.RequestException as err:
            print("Request error occurred:", err)
            return Response(
                {"error": "Request error occurred", "details": str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )