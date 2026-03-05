

from rest_framework import serializers
from merchants.serializers import KYCDocumentSerializer
from api.serializers import APIClientSerializer
from merchants.models import Merchant

class MerchantSerializer(serializers.ModelSerializer):
    kyc_documents = KYCDocumentSerializer(many=True, read_only=True)
    api_clients = APIClientSerializer(many=True, read_only=True)

    class Meta:
        model = Merchant
        fields = [
            "id",
            "merchant_id",
            "business_name",
            "business_email",
            "business_phone",
            "merchant_type",
            "website",
            "address",
            "country",
            "state",
            "registration_number",
            "is_verified",
            "kyc_documents",
            "api_clients",
        ]


class MerchantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        exclude = ['id', 'user', 'merchant_id', 'created_at', 'updated_at', 'is_verified']