from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import HealthCheckView


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]