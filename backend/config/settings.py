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
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "noreply@zootasks.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", f"ZooTasks <{EMAIL_HOST_USER}>"
)

# =============== SECURITY ===============
# Development stays HTTP-friendly; production enables HTTPS-only controls.
PRODUCTION_MODE = config("PRODUCTION_MODE", default=False, cast=bool)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=PRODUCTION_MODE, cast=bool)
SECURE_COOKIES = config("SECURE_COOKIES", default=PRODUCTION_MODE, cast=bool)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES

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

# High-assurance Owner access
OWNER_USERNAME = config("OWNER_USERNAME", default="")
OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS = config(
    "OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS", default=5, cast=int
)

LOGOUT_REDIRECT_URL = "/"
