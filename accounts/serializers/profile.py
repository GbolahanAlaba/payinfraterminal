from rest_framework import serializers
from accounts.models import Profile

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "phone",
            "gender",
            "image",
            "bio",
            "address",
            "country",
            "state",
        ]
        
class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_id",
            "phone",
            "gender",
            "image",
            "bio",
            "address",
            "country",
            "state",
            "account_type",
        ]