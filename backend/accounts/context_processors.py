from django.conf import settings


def google_oauth(request):
    """Expose only a boolean feature flag to templates, never OAuth secrets."""
    return {"GOOGLE_OAUTH_ENABLED": bool(getattr(settings, "GOOGLE_OAUTH_ENABLED", False))}
