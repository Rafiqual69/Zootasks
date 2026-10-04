import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",") if h.strip()]
INSTALLED_APPS = [

    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "accounts",
    "main",
    "tasks",
    "promotions",
    "wallet",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "accounts" / "templates", BASE_DIR / "main" / "templates", BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"

# =============== EMAIL SETTINGS ===============
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=f"ZooTasks <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else "ZooTasks",
)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=10, cast=int)

# =============== SECURITY ===============
# Development stays HTTP-friendly; production enables HTTPS-only controls.
PRODUCTION_MODE = config("PRODUCTION_MODE", default=False, cast=bool)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=PRODUCTION_MODE, cast=bool)
SECURE_COOKIES = config("SECURE_COOKIES", default=PRODUCTION_MODE, cast=bool)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = config(
    "SECURE_REFERRER_POLICY", default="same-origin"
)
SECURE_CROSS_ORIGIN_OPENER_POLICY = config(
    "SECURE_CROSS_ORIGIN_OPENER_POLICY", default="same-origin"
)
X_FRAME_OPTIONS = "DENY"

# Only enable this when a trusted reverse proxy terminates TLS and sets
# X-Forwarded-Proto after stripping any client-supplied copy.
TRUST_PROXY_SSL = config("TRUST_PROXY_SSL", default=PRODUCTION_MODE, cast=bool)
if TRUST_PROXY_SSL:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS is intentionally production-only because enabling it on an HTTP
# development host can make the host inaccessible in a browser.
SECURE_HSTS_SECONDS = config(
    "SECURE_HSTS_SECONDS",
    default=31536000 if PRODUCTION_MODE else 0,
    cast=int,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=PRODUCTION_MODE,
    cast=bool,
)
SECURE_HSTS_PRELOAD = config(
    "SECURE_HSTS_PRELOAD",
    default=PRODUCTION_MODE,
    cast=bool,
)

ASGI_APPLICATION = "config.asgi.application"

LOGIN_REDIRECT_URL = "/accounts/dashboard/"

# =============== AI SAFETY BOUNDARY ===============
# Empty by default: production AI cannot activate accidentally.
AI_PRODUCTION_APPROVED = config("AI_PRODUCTION_APPROVED", default=False, cast=bool)
AI_APPROVAL_REFERENCE = config("AI_APPROVAL_REFERENCE", default="")
AI_ALLOWED_CAPABILITIES = config("AI_ALLOWED_CAPABILITIES", default="")
AI_ALLOWED_PROVIDERS = config("AI_ALLOWED_PROVIDERS", default="")
AI_ALLOWED_MODELS = config("AI_ALLOWED_MODELS", default="")
AI_MAX_INPUT_CHARS = config("AI_MAX_INPUT_CHARS", default=12000, cast=int)
# High-assurance Owner access
OWNER_USERNAME = config("OWNER_USERNAME", default="")
OWNER_IDENTITY_EMAIL = config("OWNER_IDENTITY_EMAIL", default="")
OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS = config(
    "OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS", default=5, cast=int
)
OWNER_SOCIAL_OAUTH_STATE_TTL_SECONDS = config(
    "OWNER_SOCIAL_OAUTH_STATE_TTL_SECONDS", default=600, cast=int
)
OWNER_FACEBOOK_OAUTH_CLIENT_ID = config("OWNER_FACEBOOK_OAUTH_CLIENT_ID", default="")
OWNER_FACEBOOK_OAUTH_CLIENT_SECRET = config("OWNER_FACEBOOK_OAUTH_CLIENT_SECRET", default="")
OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT = config("OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT", default="")
OWNER_FACEBOOK_OAUTH_GRANT_TYPE = config("OWNER_FACEBOOK_OAUTH_GRANT_TYPE", default="authorization_code")
OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT = config("OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT", default="")
OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS = config("OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS", default="")
OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT = config(
    "OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT", default=""
)
OWNER_FACEBOOK_OAUTH_REDIRECT_URI = config(
    "OWNER_FACEBOOK_OAUTH_REDIRECT_URI", default=""
)
OWNER_FACEBOOK_OAUTH_SCOPES = config("OWNER_FACEBOOK_OAUTH_SCOPES", default="")
OWNER_INSTAGRAM_OAUTH_CLIENT_ID = config("OWNER_INSTAGRAM_OAUTH_CLIENT_ID", default="")
OWNER_INSTAGRAM_OAUTH_CLIENT_SECRET = config("OWNER_INSTAGRAM_OAUTH_CLIENT_SECRET", default="")
OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT = config("OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT", default="")
OWNER_INSTAGRAM_OAUTH_GRANT_TYPE = config("OWNER_INSTAGRAM_OAUTH_GRANT_TYPE", default="authorization_code")
OWNER_INSTAGRAM_OAUTH_PROFILE_ENDPOINT = config("OWNER_INSTAGRAM_OAUTH_PROFILE_ENDPOINT", default="")
OWNER_INSTAGRAM_OAUTH_PROFILE_FIELDS = config("OWNER_INSTAGRAM_OAUTH_PROFILE_FIELDS", default="")
OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT = config(
    "OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT", default=""
)
OWNER_INSTAGRAM_OAUTH_REDIRECT_URI = config(
    "OWNER_INSTAGRAM_OAUTH_REDIRECT_URI", default=""
)
OWNER_INSTAGRAM_OAUTH_SCOPES = config("OWNER_INSTAGRAM_OAUTH_SCOPES", default="")
OWNER_WEBAUTHN_RP_ID = config("OWNER_WEBAUTHN_RP_ID", default="localhost")
OWNER_WEBAUTHN_ORIGINS = tuple(
    origin.strip()
    for origin in config(
        "OWNER_WEBAUTHN_ORIGINS",
        default="http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
)
OWNER_WEBAUTHN_REAUTH_TTL_SECONDS = config(
    "OWNER_WEBAUTHN_REAUTH_TTL_SECONDS", default=600, cast=int
)
OWNER_WEBAUTHN_CHALLENGE_TTL_SECONDS = config(
    "OWNER_WEBAUTHN_CHALLENGE_TTL_SECONDS", default=120, cast=int
)

LOGOUT_REDIRECT_URL = "/"

CSRF_FAILURE_VIEW = "accounts.views.csrf_diagnostic_failure"
