from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
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
            "email",
        ]

    def validate_email(self, value):
        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value