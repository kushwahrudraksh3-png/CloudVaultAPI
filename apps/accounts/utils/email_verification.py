import secrets

from django.core.cache import cache


EMAIL_VERIFICATION_EXPIRY_SECONDS = 900
EMAIL_CHANGE_TOKEN_EXPIRY_SECONDS = 900


def generate_email_verification_token(user):
    token = secrets.token_urlsafe(32)

    redis_key = f"email_verification_token:{token}"

    token_data = {
        "user_id": user.id,
    }

    cache.set(
        redis_key,
        token_data,
        timeout=EMAIL_VERIFICATION_EXPIRY_SECONDS
    )

    return token



def generate_email_change_token(user, new_email):
    token = secrets.token_urlsafe(32)

    redis_key = f"email_change_token:{token}"

    token_data = {
        "user_id": user.id,
        "pending_email": new_email,
    }

    cache.set(
        redis_key,
        token_data,
        timeout=EMAIL_CHANGE_TOKEN_EXPIRY_SECONDS
    )

    return token