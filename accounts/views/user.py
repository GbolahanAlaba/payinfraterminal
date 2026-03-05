
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from accounts.serializers import (
    UpdateProfileSerializer, 
    ProfileSerializer,
    UserDetailSerializer
)
from accounts.models import Profile

from merchants.models import Merchant
from api.models import APIClient, ClientProvider
from modules.core.response import success_response


class UserDetailView(APIView):
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

        serializer = UserDetailSerializer(data)
        return success_response(
            serializer.data, 
            message="Data retrieved successfully", 
            status_code=status.HTTP_200_OK
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

        return success_response(serializer.data, status_code=status.HTTP_200_OK)