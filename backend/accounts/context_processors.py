from django.conf import settings


def social_login_providers(request):
    """Expose provider availability flags, never OAuth credentials."""
    return {
        "SOCIAL_LOGIN_ENABLED": getattr(settings, "SOCIAL_LOGIN_ENABLED", {}),
        "WHATSAPP_OTP_ENABLED": getattr(settings, "WHATSAPP_OTP_ENABLED", False),
    }
