from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import structlog

logger = structlog.get_logger(__name__)


def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        subject = 'Welcome to Trip Nest!'
        html_message = render_to_string('users/emails/welcome.html', {
            'user': user,
            'site_name': 'Trip Nest',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("welcome_email_sent", user_id=str(user.pk), email=user.email)
    except Exception as e:
        logger.error(
            "welcome_email_failed",
            user_id=str(user.pk),
            email=user.email,
            error=str(e),
            exc_info=True,
        )


def send_verification_email(user, verification_url=None):
    """Send email verification email"""
    try:
        if not verification_url:
            verification_url = f"http://localhost:3000/verify-email?token={user.email_verification_token}"
        
        subject = 'Verify your email address - Trip Nest'
        html_message = render_to_string('users/emails/email_verification.html', {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'Trip Nest',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("verification_email_sent", user_id=str(user.pk), email=user.email)
    except Exception as e:
        logger.error(
            "verification_email_failed",
            user_id=str(user.pk),
            email=user.email,
            error=str(e),
            exc_info=True,
        )


def send_password_reset_email(user, reset_url=None):
    """Send password reset email"""
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        if not reset_url:
            reset_url = f"http://localhost:3000/reset-password?uid={uid}&token={token}"
        
        subject = 'Reset your password - Trip Nest'
        html_message = render_to_string('users/emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'Trip Nest',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("password_reset_email_sent", user_id=str(user.pk), email=user.email)
    except Exception as e:
        logger.error(
            "password_reset_email_failed",
            user_id=str(user.pk),
            email=user.email,
            error=str(e),
            exc_info=True,
        )


def send_password_changed_email(user):
    """Send password changed notification email"""
    try:
        subject = 'Your password has been changed - Trip Nest'
        html_message = render_to_string('users/emails/password_changed.html', {
            'user': user,
            'site_name': 'Trip Nest',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(
            "password_changed_email_sent", user_id=str(user.pk), email=user.email
        )
    except Exception as e:
        logger.error(
            "password_changed_email_failed",
            user_id=str(user.pk),
            email=user.email,
            error=str(e),
            exc_info=True,
        )


def generate_username_from_email(email):
    """Generate a unique username from email"""
    from .models import User
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def calculate_profile_completion(user):
    """Calculate user profile completion percentage"""
    required_fields = [
        'first_name', 'last_name', 'phone', 'country', 'city',
        'date_of_birth'
    ]
    
    completed_fields = 0
    total_fields = len(required_fields)
    
    for field in required_fields:
        if getattr(user, field):
            completed_fields += 1
    
    # Check profile fields if profile exists
    if hasattr(user, 'profile'):
        profile_fields = ['bio', 'website']
        total_fields += len(profile_fields)
        
        for field in profile_fields:
            if getattr(user.profile, field):
                completed_fields += 1
    
    completion_percentage = (completed_fields / total_fields) * 100 if total_fields > 0 else 0
    return round(completion_percentage, 2)


def get_missing_profile_fields(user):
    """Get list of missing profile fields"""
    required_fields = [
        'first_name', 'last_name', 'phone', 'country', 'city',
        'date_of_birth'
    ]
    
    missing_fields = []
    
    for field in required_fields:
        if not getattr(user, field):
            missing_fields.append(field)
    
    return missing_fields


class EmailVerificationError(Exception):
    """Custom exception for email verification errors"""
    pass


class PasswordResetError(Exception):
    """Custom exception for password reset errors"""
    pass 