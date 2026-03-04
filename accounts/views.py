from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from accounts.serializers import (
    UpdateProfileSerializer, 
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyOTPSerializer,
    SettingsSerializer
)
from .models import Profile
from merchants.models import Merchant
from api.models import APIClient, ClientProvider



class RegisterView(APIView):
    permission_classes = []

    @transaction.atomic
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
                    "last_name": "Doe",
                    "business_name": "PayGrade Inc"
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


class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        profile = Profile.objects.select_related(
            "account_type"
        ).get(user=user)

        merchants = Merchant.objects.filter(user=user).prefetch_related(
            "kyc_documents",
            Prefetch(
                "api_clients",
                queryset=APIClient.objects.prefetch_related(
                    Prefetch(
                        "providers",
                        queryset=ClientProvider.objects.prefetch_related(
                            "credentials"
                        )
                    )
                )
            )
        )

        data = {
            "profile": profile,
            "merchants": merchants
        }

        serializer = SettingsSerializer(data)
        return Response(
            {
                "status": "success", 
                "message": "Data retrieved successfully", 
                "data": serializer.data
            }
        )
    

class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profile"],
        summary="Update User Profile",
        description="Allows authenticated users to update their profile information.",
        request=UpdateProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                name="Update Profile Example",
                value={
                    "phone": "08012345678",
                    "gender": "male",
                    "bio": "Fintech infrastructure builder",
                    "address": "Victoria Island",
                    "country": "Nigeria",
                    "state": "Lagos"
                },
                request_only=True,
            )
        ],
    )
    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)

        serializer = UpdateProfileSerializer(
            profile,
            data=request.data,
            partial=True  # Important for PATCH
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "success",
            "message": "Profile updated successfully",
            "data": ProfileSerializer(profile).data
        }, status=status.HTTP_200_OK)