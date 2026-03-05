from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from accounts.serializers import ForgotPasswordSerializer
from modules.core.response import success_response

    
class ForgotPasswordView(APIView):
    permission_classes = []

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent"),
            400: OpenApiResponse(description="User not found")
        },
        examples=[
            OpenApiExample(
                "Forgot Password Example",
                value={
                    "email": "john@example.com"
                }
            )
        ]
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)