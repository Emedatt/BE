from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(email, token):
    """
    Send email verification link to user.
    
    Args:
        email: User's email address
        token: Verification token
    """
    context = {
        'verification_url': f"{settings.FRONTEND_URL}/verify-email/{token}",
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }
    html_message = render_to_string('accounts/email/verify_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Verify Your E-MEDATT Account',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

def send_password_reset_email(email, token):
    """
    Send password reset link to user.
    
    Args:
        email: User's email address
        token: Password reset token
    """
    context = {
        'reset_url': f"{settings.FRONTEND_URL}/password-reset/confirm/{token}",
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }
    html_message = render_to_string('accounts/email/reset_password.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Reset Your E-MEDATT Password',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
