from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from apps.accounts.utils.otp import generate_password_reset_otp, generate_password_reset_token
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.utils.emailer import send_password_reset_otp
from apps.accounts.utils.email_verification import generate_email_verification_token,generate_email_change_token
from apps.accounts.utils.emailer import send_email_verification_link, send_email_change_verification_link
from apps.accounts.serializers.auth import ResendEmailVerificationSerializer


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
            
            token = generate_email_verification_token(user)

            send_email_verification_link(user.email, token)
            
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
                "timezone": user.timezone,
                "date_joined": user.date_joined,
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
                    "timezone": user.timezone,
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

            send_password_reset_otp(email, otp_data["otp"])

            return Response({
                "status": "success",
                "message": "Password reset OTP sent to your email.",
                "email": email,
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
        

class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response({
                    "status": "success",
                    "message": "Logout successful.",
                }, status=status.HTTP_200_OK)

            except Exception:
                return Response({
                    "status": "error",
                    "message": "Invalid or expired refresh token.",
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request):
        serializer = VerifyEmailSerializer(
            data={"token": request.query_params.get("token")}
        )

        if serializer.is_valid():
            token = serializer.validated_data["token"]

            redis_key = f"email_verification_token:{token}"
            token_data = cache.get(redis_key)

            if token_data is None:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid or expired verification token.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(id=token_data["user_id"])
            except User.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "User does not exist.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user.email_verified:
                return Response(
                    {
                        "status": "success",
                        "message": "Email is already verified.",
                    },
                    status=status.HTTP_200_OK,
                )

            user.email_verified = True
            user.save(update_fields=["email_verified"])

            cache.delete(redis_key)

            return Response(
                {
                    "status": "success",
                    "message": "Email verified successfully.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendEmailVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendEmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "User with this email does not exist.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user.email_verified:
                return Response(
                    {
                        "status": "error",
                        "message": "Email is already verified.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = generate_email_verification_token(user)

            send_email_verification_link(user.email, token)

            return Response(
                {
                    "status": "success",
                    "message": "Verification email sent successfully.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )



class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeEmailSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data["new_email"]

            user.pending_email = new_email
            user.save(update_fields=["pending_email"])

            token = generate_email_change_token(
                user,
                new_email
            )

            send_email_change_verification_link(
                new_email,
                token
            )

            return Response({
                "status": "success",
                "message": "Email verification link sent successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailChangeView(APIView):
    permission_classes = []

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {
                    "status": "error",
                    "message": "Verification token is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        redis_key = f"email_change_token:{token}"
        token_data = cache.get(redis_key)

        if token_data is None:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid or expired verification token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=token_data["user_id"])
        except User.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User does not exist."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        pending_email = token_data["pending_email"]

        # Check that this token is still for the user's current
        # pending email request
        if user.pending_email != pending_email:
            return Response(
                {
                    "status": "error",
                    "message": "This verification request is no longer valid."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Make sure nobody else claimed this email meanwhile
        if User.objects.filter(email=pending_email).exclude(pk=user.pk).exists():
            return Response(
                {
                    "status": "error",
                    "message": "This email address is already registered."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email = pending_email
        user.pending_email = None
        user.email_verified = True

        user.save(
            update_fields=[
                "email",
                "pending_email",
                "email_verified"
            ]
        )

        cache.delete(redis_key)

        return Response(
            {
                "status": "success",
                "message": "Email address changed and verified successfully."
            },
            status=status.HTTP_200_OK
        )
        
        
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        serializer = DeleteAccountSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():

            user = request.user

            user.delete()

            return Response({
                "status": "success",
                "message": "Account deleted successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)