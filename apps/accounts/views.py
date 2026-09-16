from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from apps.accounts.utils.otp import generate_password_reset_otp, generate_password_reset_token
from django.core.cache import cache

from .serializers.auth import *

User = get_user_model()


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "success",
            "message": "CloudVault API is running"
        })


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "status": "success",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response({
                "status": "success",
                "message": "Profile updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data["new_password"]

            user.set_password(new_password)
            user.save()

            return Response({
                "status": "success",
                "message": "Password changed successfully"
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            user = User.objects.get(email=email)

            otp_data = generate_password_reset_otp(user)

            return Response({
                "status": "success",
                "message": "Password reset OTP generated",
                "email": email,
                "otp": otp_data["otp"],
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyPasswordResetOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyPasswordResetOTPSerializer(data=request.data)

        if serializer.is_valid():
            return Response({
                "status": "success",
                "message": "OTP verified successfully",
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyPasswordResetOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyPasswordResetOTPSerializer(data=request.data)

        if serializer.is_valid():
            reset_token = serializer.validated_data["reset_token"]

            return Response({
                "status": "success",
                "message": "OTP verified successfully",
                "reset_token": reset_token,
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            reset_token = serializer.validated_data["reset_token"]
            new_password = serializer.validated_data["new_password"]

            redis_key = f"password_reset_token:{reset_token}"

            token_data = cache.get(redis_key)

            if token_data is None:
                return Response({
                    "status": "error",
                    "message": "Invalid or expired reset token.",
                }, status=status.HTTP_400_BAD_REQUEST)

            if token_data["user_id"] != User.objects.get(
                email=email
            ).id:
                return Response({
                    "status": "error",
                    "message": "Invalid reset token.",
                }, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(email=email)

            user.set_password(new_password)
            user.save()

            cache.delete(redis_key)

            return Response({
                "status": "success",
                "message": "Password reset successfully.",
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)