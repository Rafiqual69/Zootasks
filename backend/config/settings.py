import os
import re
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",") if h.strip()]

# OAuth credentials are read only from the deployment environment. Blank
# credentials keep each provider disabled; secrets are never exposed to templates.
GOOGLE_OAUTH_CLIENT_ID = config("GOOGLE_OAUTH_CLIENT_ID", default="").strip()
GOOGLE_OAUTH_CLIENT_SECRET = config("GOOGLE_OAUTH_CLIENT_SECRET", default="").strip()
FACEBOOK_OAUTH_CLIENT_ID = config("FACEBOOK_OAUTH_CLIENT_ID", default="").strip()
FACEBOOK_OAUTH_CLIENT_SECRET = config("FACEBOOK_OAUTH_CLIENT_SECRET", default="").strip()
LINKEDIN_OAUTH_CLIENT_ID = config("LINKEDIN_OAUTH_CLIENT_ID", default="").strip()
LINKEDIN_OAUTH_CLIENT_SECRET = config("LINKEDIN_OAUTH_CLIENT_SECRET", default="").strip()
YAHOO_OAUTH_CLIENT_ID = config("YAHOO_OAUTH_CLIENT_ID", default="").strip()
YAHOO_OAUTH_CLIENT_SECRET = config("YAHOO_OAUTH_CLIENT_SECRET", default="").strip()

META_WHATSAPP_ACCESS_TOKEN = config("META_WHATSAPP_ACCESS_TOKEN", default="").strip()
META_WHATSAPP_PHONE_NUMBER_ID = config("META_WHATSAPP_PHONE_NUMBER_ID", default="").strip()
META_WHATSAPP_GRAPH_API_VERSION = config(
    "META_WHATSAPP_GRAPH_API_VERSION", default="v26.0"
).strip()
META_WHATSAPP_OTP_TEMPLATE_NAME = config(
    "META_WHATSAPP_OTP_TEMPLATE_NAME", default="zootasks_login_otp"
).strip()
META_WHATSAPP_OTP_LANGUAGE_CODE = config(
    "META_WHATSAPP_OTP_LANGUAGE_CODE", default="en"
).strip()
WHATSAPP_OTP_ENABLED = bool(
    META_WHATSAPP_ACCESS_TOKEN
    and re.fullmatch(r"[0-9]{5,25}", META_WHATSAPP_PHONE_NUMBER_ID)
    and re.fullmatch(r"v[0-9]+\\.[0-9]+", META_WHATSAPP_GRAPH_API_VERSION)
    and re.fullmatch(r"[a-z0-9_]{1,512}", META_WHATSAPP_OTP_TEMPLATE_NAME)
    and re.fullmatch(r"[a-z]{2}(?:_[A-Z]{2})?", META_WHATSAPP_OTP_LANGUAGE_CODE)
)
WHATSAPP_OTP_TTL_SECONDS = 300
WHATSAPP_OTP_RESEND_SECONDS = 60
WHATSAPP_OTP_MAX_ATTEMPTS = 5
WHATSAPP_OTP_MAX_SENDS_PER_PHONE_HOUR = 5
WHATSAPP_OTP_MAX_SENDS_PER_IP_HOUR = 10

SOCIAL_LOGIN_ENABLED = {
    "google": bool(GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET),
    "facebook": bool(FACEBOOK_OAUTH_CLIENT_ID and FACEBOOK_OAUTH_CLIENT_SECRET),
    "linkedin": bool(LINKEDIN_OAUTH_CLIENT_ID and LINKEDIN_OAUTH_CLIENT_SECRET),
    "yahoo": bool(YAHOO_OAUTH_CLIENT_ID and YAHOO_OAUTH_CLIENT_SECRET),
}

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.openid_connect",
    "allauth.socialaccount.providers.yahoo",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "accounts",
    "main",
    "tasks",
    "promotions",
    "wallet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
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
                "accounts.context_processors.social_login_providers",
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

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "noreply@zootasks.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = "ZooTasks <noreply@zootasks.com>"

# =============== SOCIAL AUTHENTICATION ===============
# Keep normal password registration on the existing atomic registration view.
# Social signups use a separate adapter that provisions worker-only accounts.
ACCOUNT_ADAPTER = "accounts.account_adapter.ExistingRegistrationOnlyAccountAdapter"
SOCIALACCOUNT_ADAPTER = "accounts.adapters.SafeSocialAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = False
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = False
SOCIALACCOUNT_REQUESTS_TIMEOUT = 5

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APPS": (
            [{
                "client_id": GOOGLE_OAUTH_CLIENT_ID,
                "secret": GOOGLE_OAUTH_CLIENT_SECRET,
                "key": "",
            }]
            if SOCIAL_LOGIN_ENABLED["google"] else []
        ),
        "SCOPE": ["openid", "profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
    },
    "facebook": {
        "APPS": (
            [{
                "client_id": FACEBOOK_OAUTH_CLIENT_ID,
                "secret": FACEBOOK_OAUTH_CLIENT_SECRET,
                "key": "",
            }]
            if SOCIAL_LOGIN_ENABLED["facebook"] else []
        ),
        "METHOD": "oauth2",
        "SCOPE": ["email", "public_profile"],
        "FIELDS": ["id", "first_name", "last_name", "name", "email"],
        # Facebook email verification is not assumed.
        "VERIFIED_EMAIL": False,
    },
    "openid_connect": {
        "OAUTH_PKCE_ENABLED": True,
        "APPS": (
            [{
                "provider_id": "linkedin",
                "name": "LinkedIn",
                "client_id": LINKEDIN_OAUTH_CLIENT_ID,
                "secret": LINKEDIN_OAUTH_CLIENT_SECRET,
                "settings": {
                    "server_url": "https://www.linkedin.com/oauth",
                    "oauth_pkce_enabled": True,
                },
            }]
            if SOCIAL_LOGIN_ENABLED["linkedin"] else []
        ),
    },
    "yahoo": {
        "APPS": (
            [{
                "client_id": YAHOO_OAUTH_CLIENT_ID,
                "secret": YAHOO_OAUTH_CLIENT_SECRET,
                "key": "",
            }]
            if SOCIAL_LOGIN_ENABLED["yahoo"] else []
        ),
        "SCOPE": ["openid", "profile", "email"],
    },
}

# =============== SECURITY ===============
PRODUCTION_MODE = config("PRODUCTION_MODE", default=False, cast=bool)
SECURE_COOKIES = config("SECURE_COOKIES", default=PRODUCTION_MODE, cast=bool)
SECURE_SSL_REDIRECT = config(
    "SECURE_SSL_REDIRECT", default=PRODUCTION_MODE, cast=bool
)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
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
TRUST_PROXY_SSL = config("TRUST_PROXY_SSL", default=False, cast=bool)
if TRUST_PROXY_SSL:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ASGI_APPLICATION = "config.asgi.application"
LOGIN_REDIRECT_URL = "/accounts/dashboard/"

# Privileged Owner authentication remains password + enrolled TOTP only.
OWNER_USERNAME = config("OWNER_USERNAME", default="")
LOGOUT_REDIRECT_URL = "/"
