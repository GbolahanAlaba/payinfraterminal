from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from accounts.serializers import RegisterSerializer
from modules.core.response import success_response

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
    


