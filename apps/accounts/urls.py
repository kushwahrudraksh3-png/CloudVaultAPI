from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/register/",RegisterView.as_view(),name="register",),
    path("auth/login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/",ProfileUpdateView.as_view(),name="profile-update"),
    path("auth/change-password/",ChangePasswordView.as_view(),name="change-password"),
    path("auth/forgot-password/",ForgotPasswordView.as_view(),name="forgot-password"),
    path("auth/verify-reset-otp/", VerifyPasswordResetOTPView.as_view(), name="verify-rest-otp"),
    path("auth/reset-password/", ResetPasswordView.as_view(),name="reset-password"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/verify-email/",VerifyEmailView.as_view(), name="verify-email"),
    path("auth/resend-verification/",ResendEmailVerificationView.as_view(), name="resend-verification"),
    path("profile/change-email/", ChangeEmailView.as_view(), name="change-email"),
    path("profile/verify-email-change/", VerifyEmailChangeView.as_view(), name="verify-email-change"),
    path("profile/delete/", DeleteAccountView.as_view(), name="delete-account"),
]