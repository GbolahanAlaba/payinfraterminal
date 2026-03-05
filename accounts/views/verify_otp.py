from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from modules.core.response import success_response
from accounts.serializers import VerifyOTPSerializer

class VerifyOTPView(APIView):
    permission_classes = []
    """
    API endpoint to verify registration OTP.
    """

    @extend_schema(
        request=VerifyOTPSerializer,
        responses={
            200: OpenApiResponse(description="Email verified successfully"),
            400: OpenApiResponse(description="Invalid or expired OTP")
        },
        examples=[
            OpenApiExample(
                "Verify OTP Example",
                value={
                    "email": "john@example.com",
                    "purpose": "email",
                    "otp": "123456"
                }
            )
        ]
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid():
            result = serializer.save()

            purpose = result["purpose"]

            if purpose == "email":
                return Response(
                    {"message": "Email verified successfully. Your account is now active."},
                    status=status.HTTP_200_OK
                )

            elif purpose == "password":
                return Response(
                    {"message": "OTP verified successfully. You may now reset your password."},
                    status=status.HTTP_200_OK
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)