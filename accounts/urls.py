# urls.py
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,
    VerifyOTPView,
    UserDetailView,
    UpdateProfileAPIView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify"),
    path("auth/forgot-password/", ForgotPasswordView.as_view()),
    path("auth/reset-password/", ResetPasswordView.as_view()),
    path("profile/update/", UpdateProfileAPIView.as_view()),
    path("user/details/", UserDetailView.as_view()),
]