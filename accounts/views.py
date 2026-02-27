# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyRegistrationOTPSerializer
)



class RegisterView(APIView):
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="Registration successful"
            ),
            400: OpenApiResponse(description="Validation error")
        },
        examples=[
            OpenApiExample(
                "Register Example",
                value={
                    "email": "john@example.com",
                    "password": "strongpassword",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            )
        ],
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Registration successful. Verify email."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials")
        },
        examples=[
            OpenApiExample(
                "Login Example",
                value={
                    "email": "john@example.com",
                    "password": "strongpassword"
                }
            )
        ]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyRegistrationOTPView(APIView):
    permission_classes = []
    """
    API endpoint to verify registration OTP.
    """

    @extend_schema(
        request=VerifyRegistrationOTPSerializer,
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
        serializer = VerifyRegistrationOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Email verified successfully. Your account is now active."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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