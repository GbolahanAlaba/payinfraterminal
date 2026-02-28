
import email
import random
from attr import attrs
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, OTP
from merchants.models import Merchant
from modules.utils.emails import OnboardingEmailTasks



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    business_name = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "business_name"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        business_name = validated_data.pop("business_name")

        user = User.objects.create_user(
            password=password,
            is_active=False,
            is_approved=False,
            **validated_data
        )

        merchant = Merchant.objects.create(
            user=user,
            business_name=business_name
        )

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(
            user=user,
            code=otp_code,
            purpose="email"
        )

        # OnboardingEmailTasks.send_verify_email(user, otp_code)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive")

        if user.status in ["suspended", "flagged"]:
            raise serializers.ValidationError("Account restricted")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "status": user.status,
            }
        }

class VerifyRegistrationOTPSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    purpose = serializers.CharField(max_length=255)
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        purpose = attrs.get("purpose")
        otp_code = attrs.get("otp")

        if not email or not purpose or not otp_code:
            raise serializers.ValidationError({"detail": "Email, purpose, and OTP are required"})
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                purpose=purpose,
                is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid OTP"})

        if otp.is_expired():
            raise serializers.ValidationError({"detail": "OTP expired"})

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        user.is_approved = True
        user.is_active = True
        user.save()

        otp.is_used = True
        otp.save()

        OnboardingEmailTasks.send_verification_confirmation(user)
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(
            user=user,
            code=otp_code,
            purpose="password"
        )

        OnboardingEmailTasks.send_otp_email(user, otp_code, purpose="password")

        return {"message": "OTP sent to email"}


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp_code = attrs.get("otp")
        new_password = attrs.get("new_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                purpose="password",
                is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        if otp.is_expired():
            raise serializers.ValidationError("OTP expired")

        # Update password
        user.set_password(new_password)
        user.save()

        otp.is_used = True
        otp.save()

        return {"message": "Password reset successful"}