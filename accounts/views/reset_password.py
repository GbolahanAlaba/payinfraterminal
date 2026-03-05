from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from accounts.serializers import ResetPasswordSerializer
from modules.core.response import success_response


class ResetPasswordView(APIView):
    permission_classes = []

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Invalid OTP or user")
        },
        examples=[
            OpenApiExample(
                "Reset Password Example",
                value={
                    "email": "john@example.com",
                    "otp": "123456",
                    "new_password": "newstrongpassword"
                }
            )
        ]
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
