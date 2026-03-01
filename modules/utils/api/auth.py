from api.models.client import APIClient
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed

def authenticate_client(request):
    client_public_key = request.headers.get("X-Client-Public-Key")
    client_secret_key = request.headers.get("X-Client-Secret-Key")

    if not client_public_key or not client_secret_key:
        raise AuthenticationFailed("Missing API credentials.")

    try:
        api_client = APIClient.objects.get(client_public_key=client_public_key, status="active")
    except APIClient.DoesNotExist:
        raise AuthenticationFailed("Invalid client public key.")

    if not api_client.client_secret_key == client_secret_key: #verify_secret(client_secret):
        raise AuthenticationFailed("Invalid client secret key.")

    return api_client