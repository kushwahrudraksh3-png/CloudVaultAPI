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
    path("auth/change-password/",ChangePasswordView.as_view(),name="change-password",),
]