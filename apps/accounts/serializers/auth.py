from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from apps.accounts.utils.otp import generate_password_reset_token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "timezone",
        ]

    def validate_email(self, value):
        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")

        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)

    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Current password is incorrect."}
            )

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "New password must be different from current password."
                    )
                }
            )

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        User = get_user_model()

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account is registered with this email."
            )

        return value


class VerifyPasswordResetOTPSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate(self, attrs):

        email = attrs["email"]
        otp = attrs["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Invalid email or OTP."})

        redis_key = f"password_reset_otp:{user.id}"

        otp_data = cache.get(redis_key)

        if otp_data is None:
            raise serializers.ValidationError(
                {"otp": "OTP has expired or does not exist."}
            )

        if otp_data["attempts"] >= 5:
            raise serializers.ValidationError({"otp": "Maximum OTP attempts exceeded."})

        otp_data["attempts"] += 1

        cache.set(redis_key, otp_data, timeout=300)

        if not check_password(otp, otp_data["otp_hash"]):
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        cache.delete(redis_key)

        reset_token = generate_password_reset_token(user)

        attrs["user"] = user

        attrs["reset_token"] = reset_token

        return attrs


class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    reset_token = serializers.CharField(required=True, write_only=True)

    new_password = serializers.CharField(required=True, write_only=True, min_length=8)

    confirm_password = serializers.CharField(
        required=True, write_only=True, min_length=8
    )

    def validate(self, attrs):

        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        required=True
    )



class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    
    
class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)




class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)

    def validate_new_email(self, value):
        user = self.context["request"].user

        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        if value == user.email:
            raise serializers.ValidationError(
                "New email must be different from current email."
            )

        return value
    
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def validate_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Incorrect password."
            )

        return value
    
    
class DeactivateAccountSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def validate_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Incorrect password."
            )

        return value
    

class ReactivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def validate(self, attrs):

        email = attrs["email"]
        password = attrs["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Invalid email or password."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Invalid email or password."}
            )

        if user.is_active:
            raise serializers.ValidationError(
                {"email": "Account is already active."}
            )

        attrs["user"] = user

        return attrs
    

