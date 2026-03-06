from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from modules.core.response import success_response

from api.models import APIClient
from api.serializers import RegenerateAPIKeysSerializer

class RegenerateAPIKeysView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        """
        Regenerate API keys for a merchant's client.
        """

        try:
            api_client = APIClient.objects.get(
                id=client_id,
                merchant__user=request.user
            )
        except APIClient.DoesNotExist:
            return Response({
                "status": "error",
                "message": "API client not found."
            }, status=status.HTTP_404_NOT_FOUND)

        raw_secret = api_client.generate_credentials()

        serializer = RegenerateAPIKeysSerializer(api_client)

        response_data = serializer.data
        response_data["raw_secret"] = raw_secret

        return success_response(
            data=response_data,
            message="API keys regenerated successfully",
            status_code=status.HTTP_200_OK
        )


