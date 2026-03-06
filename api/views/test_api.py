import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TestAPIView(APIView):
    permission_classes = []

    def post(self, request):

        CLIENT_PUBLIC_KEY = "pit_pk_Sandbox_8417456a565be43b"
        CLIENT_SECRET_KEY = "pit_sk_Sandbox_isPUZD1Xlio4jZmTBexYvT1-d6GupSZUVnxaNwoz_bU"
        
        url = "http://payinfraterminal.onrender.com/v1/api/initiate-payment/"
        payload = {
            # "provider": "flutterwave",
            "provider": "paystack",
            "email": "customer@example.com", 
            "amount": 5000,                    
            "reference": "TXN123456",
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
            response.raise_for_status()
            data = response.json()
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