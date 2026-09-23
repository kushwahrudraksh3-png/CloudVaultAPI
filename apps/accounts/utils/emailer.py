from django.core.mail import send_mail
from django.conf import settings


def send_password_reset_otp(email, otp):
    """
    Send password reset OTP to user's email.
    """

    subject = "CloudVault Password Reset OTP"

    message = f"""
Hello,

Your CloudVault password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, please ignore this email.

Regards,
CloudVault Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_email_verification_link(email, token):
    subject = "Verify your CloudVault email"

    verification_link = (
        f"http://127.0.0.1:8000/api/v1/auth/verify-email/?token={token}"
    )

    message = f"""
Hello,

Thank you for registering with CloudVault.

Please verify your email address by clicking the link below:

{verification_link}

This verification link is valid for 15 minutes.

If you did not create this account, please ignore this email.

Regards,
CloudVault Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )