import secrets
from django.contrib.auth.hashers import make_password
from django.core.cache import cache


OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_password_reset_otp(user):
    """
    Generate and store a password reset OTP in Redis.
    """

    otp = str(secrets.randbelow(900000) + 100000)

    otp_hash = make_password(otp)

    redis_key = f"password_reset_otp:{user.id}"

    otp_data = {
        "otp_hash": otp_hash,
        "attempts": 0,
        "user_id": user.id,
    }

    cache.set(
        redis_key,
        otp_data,
        timeout=OTP_EXPIRY_SECONDS,
    )

    return {
        "otp": otp,
        "redis_key": redis_key,
    }


def generate_password_reset_token(user):
    """
    Generate and store a temporary password reset token in Redis.
    """

    token = secrets.token_urlsafe(32)

    redis_key = f"password_reset_token:{token}"

    token_data = {
        "user_id": user.id,
    }

    cache.set(
        redis_key,
        token_data,
        timeout=300,
    )

    return token