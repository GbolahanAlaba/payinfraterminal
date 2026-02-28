from api.models.client import APIClient
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed

def authenticate_client(request):
    client_id = request.headers.get("X-Client-Id")
    client_secret = request.headers.get("X-Client-Secret")

    if not client_id or not client_secret:
        raise AuthenticationFailed("Missing API credentials.")

    try:
        api_client = APIClient.objects.get(client_id=client_id, status="active")
    except APIClient.DoesNotExist:
        raise AuthenticationFailed("Invalid client_id.")

    if not check_password(client_secret, api_client.client_secret):
        raise AuthenticationFailed("Invalid client_secret.")

    return api_client