from api.models.client import APIClient
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed

def authenticate_client(request):
    client_secret_key = request.headers.get("Client-Secret-Key")

    if not client_secret_key:
        raise AuthenticationFailed("Missing API credentials.")
    try:
        api_client = APIClient.objects.get(client_secret_key=client_secret_key, status="active")
    except APIClient.DoesNotExist:
        raise AuthenticationFailed("Invalid client secret key.")

    if not api_client.client_secret_key == client_secret_key: #verify_secret(client_secret):
        raise AuthenticationFailed("Invalid client secret key.")

    if client_secret_key.startswith("pit_sk_live"):
        if not api_client.merchant.live_mode:
            raise AuthenticationFailed(
                "You currently provided live keys but your account is not in live mode."
            )

    return api_client



# def authenticate_client(request):
#     client_public_key = request.headers.get("Client-Public-Key")
#     client_secret_key = request.headers.get("Client-Secret-Key")

#     if not client_public_key or not client_secret_key:
#         raise AuthenticationFailed("Missing API credentials.")
#     try:
#         public_env = client_public_key.split("_")[2].lower()
#         secret_env = client_secret_key.split("_")[2].lower()

#         if public_env != secret_env:
#             raise AuthenticationFailed("Public key and secret key do not match.")
#     except IndexError:
#         raise AuthenticationFailed("Invalid API key format.")
#     try:
#         api_client = APIClient.objects.get(client_public_key=client_public_key, status="active")
#     except APIClient.DoesNotExist:
#         raise AuthenticationFailed("Invalid client public key.")

#     if not api_client.client_secret_key == client_secret_key: #verify_secret(client_secret):
#         raise AuthenticationFailed("Invalid client secret key.")

#     if client_public_key.startswith("pit_pk_live") and client_secret_key.startswith("pit_sk_live"):
#         if not api_client.merchant.live_mode:
#             raise AuthenticationFailed(
#                 "You currently provided live keys but your account is not in live mode."
#             )

#     return api_client