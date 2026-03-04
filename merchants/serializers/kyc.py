from rest_framework import serializers
from merchants.models import KYCDocument


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = [
            "id",
            "document_type",
            "document_file",
            "verified",
            "uploaded_at",
        ]